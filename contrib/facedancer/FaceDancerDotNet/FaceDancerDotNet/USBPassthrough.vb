Imports System.Text.Encoding
'THIS CLASS ISN'T QUITE FINISHED AND MAY STILL HAVE SOME TEST CODE IN IT
Public Class USBPassthroughDevice
    Inherits USBDevice

    Public baseDevice As LibUsbDotNet.UsbDevice

    Public Sub New(device As LibUsbDotNet.UsbDevice, maxusb_app As MAXUSBApp, Optional verbose As Byte = 0)
        MyBase.New()
        Me.maxusb_app = maxusb_app
        Me.verbose = verbose
        Me.strings = New List(Of String)
        Me.baseDevice = device


        Dim buf(1024) As Byte
        Dim buflen As Integer
        If Not device.GetDescriptor(LibUsbDotNet.Descriptors.DescriptorType.Device, 0, 0, buf, 1024, buflen) Then Stop

        Me.usb_spec_version = buf(2) * 256 + buf(3)
        Me.usb_spec_version = 1
        Me.device_class = buf(4)
        Me.device_subclass = buf(5)
        Me.protocol_rel_num = buf(6)
        Me.max_packet_size_ep0 = buf(7)
        Me.vendor_id = buf(8) + buf(9) * 256
        Me.product_id = buf(10) + buf(11) * 256
        Me.device_rev = buf(12) + buf(13) * 256
        Me.manufacturer_string_id = buf(14)
        Me.product_string_id = buf(15)
        Me.serial_number_string_id = buf(16)
        Dim tmp As String = vbNullString
        device.GetString(tmp, 1033, Me.product_string_id)
        Me.name = "PASSTHROUGH " & tmp

        '***
        'Me.vendor_id = &H6666
        'Me.product_id = &H6666
        Me.max_packet_size_ep0 = 64
        'Me.product_id = Me.product_id + 1

        Dim configCount As Byte = buf(17)
        If Me.descriptors.ContainsKey(USB.desc_type._device) Then Me.descriptors(USB.desc_type._device) = AddressOf Me.get_descriptor Else Me.descriptors.Add(USB.desc_type._device, AddressOf Me.get_descriptor)
        If Me.descriptors.ContainsKey(USB.desc_type._string) Then Me.descriptors(USB.desc_type._string) = AddressOf Me.passthrough_get_string_descriptor_request Else Me.descriptors.Add(USB.desc_type._string, AddressOf Me.passthrough_get_string_descriptor_request)
        If Me.descriptors.ContainsKey(USB.desc_type._configuration) Then Me.descriptors(USB.desc_type._configuration) = AddressOf Me.handle_get_configuration_descriptor_request Else Me.descriptors.Add(USB.desc_type._configuration, AddressOf Me.handle_get_configuration_descriptor_request)

        For Each c As LibUsbDotNet.Info.UsbConfigInfo In baseDevice.Configs
            Me.configurations.Add(c.Descriptor.ConfigID, New USBPassthroughConfiguration(c, baseDevice))
            Me.configurations(c.Descriptor.ConfigID).set_device(Me)
        Next
        Me.config_num = -1
        Me.configuration = Nothing

        Me.state = USB.state._detached
        Me.ready = False
        Me.address = 0

        setup_request_handlers()

        Me.device_vendor = New USBPassthroughVendor(baseDevice)
        Me.device_vendor.set_device(Me)
    End Sub

    Function passthrough_get_string_descriptor_request(req As USBDeviceRequest) As Byte()
        Dim tmp As String = vbNullString
        Dim num As Byte = req.value And 255
        baseDevice.GetString(tmp, req.index, num)
        Dim s() As Byte = Unicode.GetBytes(tmp)
        Dim d(s.Length + 1) As Byte
        d(0) = d.Length
        d(1) = 3
        Array.Copy(s, 0, d, 2, s.Length)
        Return d
    End Function


End Class

Public Class USBPassthroughVendor
    Inherits USBVendor
    Implements IRequest_Handler

    Public baseDevice As LibUsbDotNet.UsbDevice

    Public Sub New(baseDevice As LibUsbDotNet.UsbDevice, Optional verbose As Byte = 0)
        Me.baseDevice = baseDevice
    End Sub

    Public Overrides Sub setup_request_handlers()
        request_handlers.Add(&H1, AddressOf passthrough_request_handler)
        request_handlers.Add(&H81, AddressOf passthrough_request_handler)
        request_handlers.Add(&H82, AddressOf passthrough_request_handler)
        request_handlers.Add(&H83, AddressOf passthrough_request_handler)
        request_handlers.Add(&H84, AddressOf passthrough_request_handler)
        request_handlers.Add(&H86, AddressOf passthrough_request_handler)
        request_handlers.Add(&H87, AddressOf passthrough_request_handler)
        request_handlers.Add(&HA1, AddressOf passthrough_request_handler)
        request_handlers.Add(&HA9, AddressOf passthrough_request_handler)
    End Sub

    Public Function convertUSBSetupPacket(req As USBDeviceRequest) As LibUsbDotNet.Main.UsbSetupPacket

    End Function

    Public Sub passthrough_request_handler(req As USBDeviceRequest)
        Dim value As Int16 = 0
        Dim index As Int16 = 0
        Dim length As Int16 = 0
        If req.value > Int16.MaxValue Then value = req.value - 65536 Else value = req.value
        If req.index > Int16.MaxValue Then index = req.index - 65536 Else index = req.index
        If req.length > Int16.MaxValue Then length = req.length - 65536 Else length = req.length
        Dim p As New LibUsbDotNet.Main.UsbSetupPacket(req.request_type, req.request, value, index, length)
        If req.request = 161 Or req.request = 169 Then Stop
        If req.get_direction Then
            Dim buf(req.length - 1) As Byte
            Dim lt As Integer
            If Not baseDevice.ControlTransfer(p, buf, buf.Length, lt) Then Debug.Print("LibUSB Control Transfer Error: " & LibUsbDotNet.UsbDevice.LastErrorString)
            If lt < buf.Length Then ReDim Preserve buf(lt - 1)
            device.maxusb_app.verbose += 1
            '***Why is this necessary***
            device.maxusb_app.read_register(MAXUSBApp.reg._ep0_byte_count)
            If req.length > 0 Then device.maxusb_app.send_on_endpoint(0, buf, device.max_packet_size_ep0) Else Stop
            device.maxusb_app.verbose -= 1
        Else
            Dim buf() As Byte
            If req.length > 0 Then
                device.maxusb_app.verbose += 1
                buf = device.maxusb_app.read_from_endpoint(0)
                device.maxusb_app.verbose -= 1
            Else
                buf = New Byte() {}
            End If
            Dim lt As Integer
            If Not baseDevice.ControlTransfer(p, buf, buf.Length, lt) Then Debug.Print("LibUSB Control Transfer Error: " & LibUsbDotNet.UsbDevice.LastErrorString)
            device.maxusb_app.ack_status_stage()
        End If
    End Sub
End Class

Public Class USBPassthroughConfiguration
    Inherits USBConfiguration

    Public customDescriptors As New List(Of Byte())

    Public Sub New(baseConfig As LibUsbDotNet.Info.UsbConfigInfo, baseDevice As LibUsbDotNet.UsbDevice)
        Me.configuration_index = baseConfig.Descriptor.ConfigID
        Me.configuration_string = baseConfig.ConfigString
        Me.configuration_string_index = baseConfig.Descriptor.StringIndex
        Me.attributes = baseConfig.Descriptor.Attributes
        Me.max_power = baseConfig.Descriptor.MaxPower
        Me.device = Nothing

        For Each desc As Byte() In baseConfig.CustomDescriptors
            customDescriptors.Add(desc)
        Next

        For Each i As LibUsbDotNet.Info.UsbInterfaceInfo In baseConfig.InterfaceInfoList
            Me.interfaces.Add(i.Descriptor.InterfaceID, New USBPassthroughInterface(i, baseDevice))
            Me.interfaces(i.Descriptor.InterfaceID).set_configuration(Me)
        Next
    End Sub

    Public Overrides Function get_descriptor(n As Byte) As Byte()
        Dim interface_descriptors As New List(Of Byte)
        interface_descriptors.AddRange(New Byte() {9, 2, 0, 0, Me.interfaces.Count, Me.configuration_index, Me.configuration_string_index, Me.attributes, Me.max_power})
        For Each desc As Byte() In customDescriptors
            interface_descriptors.AddRange(desc)
        Next

        For Each i As USBInterface In interfaces.Values
            interface_descriptors.AddRange(i.get_descriptor(0))
        Next
        Dim total_len As UInt16 = interface_descriptors.Count
        interface_descriptors(2) = total_len And 255
        interface_descriptors(3) = total_len \ 256 And 255
        Return interface_descriptors.ToArray
    End Function
End Class

Public Class USBPassthroughInterface
    Inherits USBInterface
    Public customDescriptors As New List(Of Byte())

    Public Sub New(baseInterface As LibUsbDotNet.Info.UsbInterfaceInfo, baseDevice As LibUsbDotNet.UsbDevice, Optional verbose As Byte = 0)
        Me.verbose = verbose
        Me.number = baseInterface.Descriptor.InterfaceID
        Me.name = "Interface " & Me.number

        Me.alternate = baseInterface.Descriptor.AlternateID
        Me.iclass = baseInterface.Descriptor.Class
        Me.subclass = baseInterface.Descriptor.SubClass
        Me.protocol = baseInterface.Descriptor.Protocol
        Me.string_index = baseInterface.Descriptor.StringIndex

        Me.configuration = Nothing
        Me.device_class = Nothing

        If Me.descriptors.ContainsKey(USB.desc_type._interface) Then Me.descriptors(USB.desc_type._interface) = AddressOf Me.get_descriptor Else Me.descriptors.Add(USB.desc_type._interface, AddressOf Me.get_descriptor)

        For Each desc As Byte() In baseInterface.CustomDescriptors
            customDescriptors.Add(desc)
        Next

        For i As Integer = 0 To baseInterface.EndpointInfoList.Count - 1
            Dim idx As Byte = baseInterface.EndpointInfoList(i).Descriptor.EndpointID
            Dim tmp As New USBPassthroughEndpoint(baseInterface.EndpointInfoList(i), baseDevice)
            tmp.set_interface(Me)
            Me.endpoints.Add(idx, tmp)
        Next

        Me.request_handlers.Add(6, AddressOf handle_get_descriptor_request)
        Me.request_handlers.Add(11, AddressOf handle_set_interface_request)
    End Sub

    Public Overrides Function get_descriptor(n As Byte) As Byte()
        Dim d As New List(Of Byte)
        d.AddRange(New Byte() {9, 4, Me.number, Me.alternate, Me.endpoints.Count, Me.iclass, Me.subclass, Me.protocol, Me.string_index})
        If Me.iclass Then
            Dim iclass_desc_num As Byte = USB.interface_class_to_descriptor_type(Me.iclass)
            If iclass_desc_num > 0 Then d.AddRange(Me.descriptors(iclass_desc_num)(n))
        End If
        For Each desc As Byte() In customDescriptors
            d.AddRange(desc)
        Next
        For Each e As USBEndpoint In Me.endpoints.Values
            d.AddRange(e.get_descriptor(0))
        Next e
        Return d.ToArray
    End Function

End Class

Public Class USBPassthroughEndpoint
    Inherits USBEndpoint
    Public baseDevice As LibUsbDotNet.UsbDevice
    Public address As Byte

    Public Sub New(baseEndpoint As LibUsbDotNet.Info.UsbEndpointInfo, baseDevice As LibUsbDotNet.UsbDevice)
        Me.baseDevice = baseDevice
        Me.max_packet_size = baseEndpoint.Descriptor.MaxPacketSize
        Me.interval = baseEndpoint.Descriptor.Interval
        Me.address = baseEndpoint.Descriptor.EndpointID
        Me.direction = Me.address \ 128
        Me.number = Me.address And &HF

        Dim attributes As Byte = baseEndpoint.Descriptor.Attributes
        Me.transfer_type = attributes And &H3
        Me.sync_type = (attributes \ 4) And &H3
        Me.usage_type = (attributes \ 16) And &H3

        Me.handler = AddressOf Me.handle_data
        Me._interface = Nothing
        request_handlers.Add(1, AddressOf Me.handle_clear_feature_request)
    End Sub

    Public Sub handle_data(data() As Byte)
        If Me.direction = enum_direction._in Then
            If data Is Nothing Then Exit Sub
            Dim tl As Integer = 0
            Dim ew As LibUsbDotNet.UsbEndpointWriter = baseDevice.OpenEndpointWriter(Me.number)
            Dim ec As LibUsbDotNet.Main.ErrorCode = ew.Transfer(data, 0, data.Length, 1000, tl)
            If ec <> LibUsbDotNet.Main.ErrorCode.Success Then Stop
        End If
        If Me.direction = enum_direction._out Then
            Dim buf(1024) As Byte
            Dim tl As Integer = 0
            Dim er As LibUsbDotNet.UsbEndpointReader = baseDevice.OpenEndpointReader(Me.number)
            Dim ec As LibUsbDotNet.Main.ErrorCode = er.Transfer(buf, 0, buf.Length, 1000, tl)
            If ec <> LibUsbDotNet.Main.ErrorCode.Success Then Stop
            If tl = 0 Then Exit Sub
            Dim tmp(tl - 1) As Byte
            Array.Copy(buf, 0, tmp, 0, tl)
            Me._interface.configuration.device.maxusb_app.send_on_endpoint(Me.number, tmp, Me.max_packet_size)
            Debug.Print("Sent EP" & Me.number & " " & BitConverter.ToString(buf))
        End If
    End Sub
End Class