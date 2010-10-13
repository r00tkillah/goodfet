#############################
# Transaction Values
#   0 = Request
#   1 = Response
#############################
TRANSACTION = 0
#############################

#############################
# SPI Byte Values
#############################
spi_version_mask = 0xC0
spi_pro_stat = (0x0A, 0x0B, 0xC0, 0xC1)

spi_bytes = (
    0x00,
    0x01,
    0x02,
    0x03,
    0x04,
    0x0A,
    0x0B,
    0xC0,
    0xC1,
    0xA7,
    0xFD,
    0xFE,
    0xFF
)

spi_values = (
    'EM260_RESET',
    'OVERSIZED_EZSP_FRAME',
    'ABORTED_TRANSACTION',
    'MISSING_FRAME_TERMINATOR',
    'RESERVED_ERROR',
    'SPI_PROTOCOL_VERSION',
    'SPI_STATUS',
    'RESP_STAT_SLEEP',
    'RESP_STAT_READY',
    'FRAME_TERMINATOR',
    'BOOTLOADER_FRAME',
    'EZSP_FRAME',
    'CONT_BYTE'
)

spi_table = {}
spi_table_rev = {}
for byte in xrange(len(spi_bytes)):
    spi_table[spi_bytes[byte]] = spi_values[byte]
    spi_table_rev[spi_values[byte]] = spi_bytes[byte]

#############################

#############################
# Command Control Frame
#############################
cmd_mask = 0x80
resp_over_mask = 0x01
resp_trun_mask = 0x02

cmd_control = (
    'CMDI',       # Master State: Idle
    'CMDD',       # Master State: Deep Sleep
    'CMDP',       # Master State: Power Down
    'Reserved',
    'Reserved',
    'Reserved',
    'Reserved',
)

#resp_overflow = 'Out of Memory'
resp_overflow = 'NOMEM'
#resp_truncated = 'Truncated Response'
resp_truncated = 'TRUNC_RESP'
#############################

#############################
# Named Values
#############################

# Ember

# Boolean
boolean = (
    'FALSE',      # 0x00
    'TRUE'        # 0x01
)

# Frame IDs
frame_error = 'NOT IMPLEMENTED'
frame_ids = (
    'version',                  # 0x00
    'NOT IMPLEMENTED',          # 0x01
    'addEndpoint',              # 0x02
    'NOT IMPLEMENTED',          # 0x03
    'NOT IMPLEMENTED',          # 0x04
    'nop',                      # 0x05
    'callback',                 # 0x06
    'noCallbacks',              # 0x07
    'reset',                    # 0x08
    'setToken',                 # 0x09
    'getToken',                 # 0x0A
    'getMfgToken',              # 0x0B
    'NOT IMPLEMENTED',          # 0x0C
    'getMillisecondTime',       # 0x0D
    'setTimer',                 # 0x0E
    'timerHandler',             # 0x0F
    'serialWrite',              # 0x10
    'serialRead',               # 0x11
    'debugWrite',               # 0x12
    'debugHandler',             # 0x13
    'requestLinkKey',           # 0x14
    'setManufacturerCode',      # 0x15
    'setPowerDescriptor',       # 0x16
    'networkInit',              # 0x17
    'networkState',             # 0x18
    'stackStatusHandler',       # 0x19
    'startScan',                # 0x1A
    'networkFoundHandler',      # 0x1B
    'scanCompleteHandler',      # 0x1C
    'stopScan',                 # 0x1D
    'formNetwork',              # 0x1E
    'joinNetwork',              # 0x1F
    'leaveNetwork',             # 0x20
    'findAndRejoinNetwork',     # 0x21
    'permitJoining',            # 0x22
    'childJoinHandler',         # 0x23
    'trustCenterJoinHandler',   # 0x24
    'NOT IMPLEMENTED',          # 0x25
    'getEui64',                 # 0x26
    'getNodeId',                # 0x27
    'getNetworkParameters',     # 0x28
    'getParentChildParameters', # 0x29
    'clearBindingTable',        # 0x2A
    'setBinding',               # 0x2B
    'getBinding',               # 0x2C
    'deleteBinding',            # 0x2D
    'bindingIsActive',          # 0x2E
    'getBindingRemoteNodeId',   # 0x2F
    'setBindingRemoteNodeId',   # 0x30
    'remoteSetBindingHandler',  # 0x31
    'remoteDeleteBindingHandler',   # 0x32
    'maximumPayloadLength',     # 0x33
    'sendUnicast',              # 0x34
    'NOT IMPLEMENTED',          # 0x35
    'sendBroadcast',            # 0x36
    'NOT IMPLEMENTED',          # 0x37
    'sendMulticast',            # 0x38
    'sendReply',                # 0x39
    'NOT IMPLEMENTED',          # 0x3A
    'NOT IMPLEMENTED',          # 0x3B
    'NOT IMPLEMENTED',          # 0x3C
    'NOT IMPLEMENTED',          # 0x3D
    'NOT IMPLEMENTED',          # 0x3E
    'messageSentHandler',       # 0x3F
    'cancelMessage',            # 0x40
    'sendManyToOneRouteRequest',# 0x41
    'pollForData',              # 0x42
    'pollCompleteHandler',      # 0x43
    'pollHandler',              # 0x44
    'incomingMessageHandler',   # 0x45
    'setRam',                   # 0x46
    'getRam',                   # 0x47
    'energyScanResultHandler',  # 0x48
    'getRandomNumber',          # 0x49
    'getChildData',             # 0x4A
    'NOT IMPLEMENTED',          # 0x4B
    'NOT IMPLEMENTED',          # 0x4C
    'NOT IMPLEMENTED',          # 0x4D
    'getTimer',                 # 0x4E
    'scanAndFormNetwork',       # 0x4F
    'scanAndJoinNetwork',       # 0x50
    'scanErrorHandler',         # 0x51
    'getConfigurationValue',    # 0x52
    'setConfigurationValue',    # 0x53
    'NOT IMPLEMENTED',          # 0x54
    'setPolicy',                # 0x55
    'getPolicy',                # 0x56
    'NOT IMPLEMENTED',          # 0x57
    'invalidCommand',           # 0x58
    'incomingRouteRecordHandler',   # 0x59
    'setSourceRoute',           # 0x5A
    'addressTableEntryIsActive',# 0x5B
    'setAddressTableRemoteEui64',   # 0x5C
    'setAddressTableRemoteNodeId',  # 0x5D
    'getAddressTableRemoteEui64',   # 0x5E
    'getAddressTableRemoteNodeId',  # 0x5F
    'lookupNodeIdByEui64',      # 0x60
    'lookupEui64ByNodeId',      # 0x61
    'incomingSenderEui64Handler',   # 0x62
    'getMulticastTableEntry',   # 0x63
    'setMulticastTableEntry',   # 0x64
    'readAndClearCounters',     # 0x65
    'addOrUpdateKeyTableEntry', # 0x66
    'NOT IMPLEMENTED',          # 0x67
    'setInitialSecurityState',  # 0x68
    'getCurrentSecurityState',  # 0x69
    'getKey',                   # 0x6A
    'NOT IMPLEMENTED',          # 0x6B
    'NOT IMPLEMENTED',          # 0x6C
    'NOT IMPLEMENTED',          # 0x6D
    'switchNetworkKeyHandler',  # 0x6E
    'NOT IMPLEMENTED',          # 0x6F
    'NOT IMPLEMENTED',          # 0x70
    'getKeyTableEntry',         # 0x71
    'setKeyTableEntry',         # 0x72
    'broadcastNextNetworkKey',  # 0x73
    'broadcastNetworkKeySwitch',# 0x74
    'findKeyTableEntry',        # 0x75
    'eraseKeyTableEntry',       # 0x76
    'becomeTrustCenter',        # 0x77
    'NOT IMPLEMENTED',          # 0x78
    'getNeighbor',              # 0x79
    'neighborCount',            # 0x7A
    'getRouteTableEntry',       # 0x7B
    'idConflictHandler',        # 0x7C
    'incomingManyToOneRouteRequestHandler', # 0x7D
    'setExtendedTimeout',       # 0x7E
    'getExtendedTimeout',       # 0x7F
    'incomingRouteErrorHandler',# 0x80
    'echo',                     # 0x81
    'replaceAddressTableEntry', # 0x82
    'mfglibStart',              # 0x83
    'mfglibEnd',                # 0x84
    'mfglibStartTone',          # 0x85
    'mfglibStopTone',           # 0x86
    'mfglibStartStream',        # 0x87
    'mfglibStopStream',         # 0x88
    'mfglibSendPacket',         # 0x89
    'mfglibSetChannel',         # 0x8A
    'mfglibGetChannel',         # 0x8B
    'mfglibSetPower',           # 0x8C
    'mfglibGetPower',           # 0x8D
    'mfglibRxHandler',          # 0x8E
    'launchStandaloneBootloader',   # 0x8F
    'sendBootloadMessage',      # 0x90
    'getStandaloneBootloaderVersionPlatMicroPhy',   # 0x91
    'incomingBootloadMessageHandler',   # 0x92
    'bootloadTransmitCompleteHandler',  # 0x93
    'aesEncrypt',               # 0x94
    'overrideCurrentChannel',   # 0x95
    'sendRawMessage',           # 0x96
    'macPassthroughMessageHandler', # 0x97
    'rawTransmitCompleteHandler',   # 0x98
    'setRadioPower',            # 0x99
    'setRadioChannel',          # 0x9A
    'zigbeeKeyEstablishmentHandler',    # 0x9B
    'energyScanRequest',        # 0x9C
    'delayTest',                # 0x9D
    'generateCbkeKeysHandler',  # 0x9E
    'calculateSmacs',           # 0x9F
    'calculateSmacsHandler',    # 0xA0
    'clearTemporaryDataMaybeStoreLinkKey',  # 0xA1
    'NOT IMPLEMENTED',          # 0xA2
    'NOT IMPLEMENTED',          # 0xA3
    'generateCbkeKeys',         # 0xA4
    'NOT IMPLEMENTED',          # 0xA5
    'dsaSign',                  # 0xA6
    'dsaSignHandler',           # 0xA7
    'scanForJoinableNetwork',   # 0xA8
    'unusedPanIdFoundHandler',  # 0xA9
    'getValue',                 # 0xAA
    'setValue',                 # 0xAB
    'NOT IMPLEMENTED',          # 0xAC
    'NOT IMPLEMENTED',          # 0xAD
    'NOT IMPLEMENTED',          # 0xAE
    'NOT IMPLEMENTED'           # 0xAF
)

frame_table = {}
frame_table_rev = {}
for fid in xrange(len(frame_ids)):
    frame_table[fid] = frame_ids[fid]
    frame_table[frame_ids[fid]] = fid

# EzspConfigId
EZSP_CONFIG_PACKET_BUFFER_COUNT         = 0x01
EZSP_CONFIG_NEIGHBOR_TABLE_SIZE         = 0x02
EZSP_CONFIG_APS_UNICAST_MESSAGE_COUNT   = 0x03
EZSP_CONFIG_BINDING_TABLE_SIZE          = 0x04
EZSP_CONFIG_ADDRESS_TABLE_SIZE          = 0x05
EZSP_CONFIG_MULTICAST_TABLE_SIZE        = 0x06
EZSP_CONFIG_ROUTE_TABLE_SIZE            = 0x07
EZSP_CONFIG_DISCOVERY_TABLE_SIZE        = 0x08
EZSP_CONFIG_BROADCAST_ALARM_DATA_SIZE   = 0x09
EZSP_CONFIG_UNICAST_ALARM_DATA_SIZE     = 0x0A
EZSP_CONFIG_STACK_PROFILE               = 0x0C
EZSP_CONFIG_SECURITY_LEVEL              = 0x0D
EZSP_CONFIG_MAX_HOPS                    = 0x10
EZSP_CONFIG_MAX_END_DEVICE_CHILDREN     = 0x11
EZSP_CONFIG_INDIRECT_TRANSMISSION_TIMEOUT = 0x12
EZSP_CONFIG_END_DEVICE_POLL_TIMEOUT     = 0x13
EZSP_CONFIG_MOBILE_NODE_POLL_TIMEOUT    = 0x14
EZSP_CONFIG_RESERVED_MOBILE_CHILD_ENTRIES = 0x15
EZSP_CONFIG_HOST_RAM                    = 0x16
EZSP_CONFIG_TX_POWER_MODE               = 0x17
EZSP_CONFIG_DISABLE_RELAY               = 0x18
EZSP_CONFIG_TRUST_CENTER_ADDRESS_CACHE_SIZE = 0x19
EZSP_CONFIG_SOURCE_ROUTE_TABLE_SIZE     = 0x1A
EZSP_CONFIG_END_DEVICE_POLL_TIMEOUT_SHIFT = 0x1B
EZSP_CONFIG_FRAGMENT_WINDOW_SIZE        = 0x1C
EZSP_CONFIG_FRAGMENT_DELAY_MS           = 0x1D
EZSP_CONFIG_KEY_TABLE_SIZE              = 0x1E
EZSP_CONFIG_APS_ACK_TIMEOUT             = 0x1F
EZSP_CONFIG_ACTIVE_SCAN_DURATION        = 0x20
EZSP_CONFIG_END_DEVICE_BIND_TIMEOUT     = 0x21
EZSP_CONFIG_PAN_ID_CONFLICT_REPORT_THRESHOLD = 0x22
EZSP_CONFIG_REQUEST_KEY_TIMEOUT         = 0x24
EZSP_CONFIG_ENABLE_DUAL_CHANNEL_SCAN    = 0x25

ezsp_config_id = {
	'EZSP_CONFIG_PACKET_BUFFER_COUNT'         : 0x01,\
	'EZSP_CONFIG_NEIGHBOR_TABLE_SIZE'         : 0x02,\
	'EZSP_CONFIG_APS_UNICAST_MESSAGE_COUNT'   : 0x03,\
	'EZSP_CONFIG_BINDING_TABLE_SIZE'          : 0x04,\
	'EZSP_CONFIG_ADDRESS_TABLE_SIZE'          : 0x05,\
	'EZSP_CONFIG_MULTICAST_TABLE_SIZE'        : 0x06,\
	'EZSP_CONFIG_ROUTE_TABLE_SIZE'            : 0x07,\
	'EZSP_CONFIG_DISCOVERY_TABLE_SIZE'        : 0x08,\
	'EZSP_CONFIG_BROADCAST_ALARM_DATA_SIZE'   : 0x09,\
	'EZSP_CONFIG_UNICAST_ALARM_DATA_SIZE'     : 0x0A,\
	'EZSP_CONFIG_STACK_PROFILE'               : 0x0C,\
	'EZSP_CONFIG_SECURITY_LEVEL'              : 0x0D,\
	'EZSP_CONFIG_MAX_HOPS'                    : 0x10,\
	'EZSP_CONFIG_MAX_END_DEVICE_CHILDREN'     : 0x11,\
	'EZSP_CONFIG_INDIRECT_TRANSMISSION_TIMEOUT' : 0x12,\
	'EZSP_CONFIG_END_DEVICE_POLL_TIMEOUT'     : 0x13,\
	'EZSP_CONFIG_MOBILE_NODE_POLL_TIMEOUT'    : 0x14,\
	'EZSP_CONFIG_RESERVED_MOBILE_CHILD_ENTRIES' : 0x15,\
	'EZSP_CONFIG_HOST_RAM'                    : 0x16,\
	'EZSP_CONFIG_TX_POWER_MODE'               : 0x17,\
	'EZSP_CONFIG_DISABLE_RELAY'               : 0x18,\
	'EZSP_CONFIG_TRUST_CENTER_ADDRESS_CACHE_SIZE' : 0x19,\
	'EZSP_CONFIG_SOURCE_ROUTE_TABLE_SIZE'     : 0x1A,\
	'EZSP_CONFIG_END_DEVICE_POLL_TIMEOUT_SHIFT' : 0x1B,\
	'EZSP_CONFIG_FRAGMENT_WINDOW_SIZE'        : 0x1C,\
	'EZSP_CONFIG_FRAGMENT_DELAY_MS'           : 0x1D,\
	'EZSP_CONFIG_KEY_TABLE_SIZE'              : 0x1E,\
	'EZSP_CONFIG_APS_ACK_TIMEOUT'             : 0x1F,\
	'EZSP_CONFIG_ACTIVE_SCAN_DURATION'        : 0x20,\
	'EZSP_CONFIG_END_DEVICE_BIND_TIMEOUT'     : 0x21,\
	'EZSP_CONFIG_PAN_ID_CONFLICT_REPORT_THRESHOLD' : 0x22,\
	'EZSP_CONFIG_REQUEST_KEY_TIMEOUT'         : 0x24,\
	'EZSP_CONFIG_ENABLE_DUAL_CHANNEL_SCAN'    : 0x25,\
    }
ezsp_config_id_rev = {}
for cid,num in ezsp_config_id.items():
    ezsp_config_id_rev[num] = cid

# EzspValueId
EZSP_VALUE_TOKEN_STACK_NODE_DATA        = 0x00
EZSP_VALUE_MAC_PASSTHROUGH_FLAGS        = 0x01
EZSP_VALUE_EMBERNET_PASSTHROUGH_SOURCE_ADDRESS = 0x02
ezsp_value_id = {\
    'EZSP_VALUE_TOKEN_STACK_NODE_DATA'        : 0x00,\
    'EZSP_VALUE_MAC_PASSTHROUGH_FLAGS'        : 0x01,\
    'EZSP_VALUE_EMBERNET_PASSTHROUGH_SOURCE_ADDRESS' : 0x02,\
}
ezsp_value_id_rev = {}
for vid,num in ezsp_value_id.items():
    ezsp_value_id_rev[num] = vid

# EmberConfigTxPowerMode
EMBER_TX_POWER_MODE_DEFAULT             = 0x00
EMBER_TX_POWER_MODE_BOOST               = 0x01
EMBER_TX_POWER_MODE_ALTERNATE           = 0x02
EMBER_TX_POWER_MODE_BOOST_AND_ALTERNATE = 0x03

ember_config_tx_power_mode = {\
    'EMBER_TX_POWER_MODE_DEFAULT'             : 0x00,\
    'EMBER_TX_POWER_MODE_BOOST'               : 0x01,\
    'EMBER_TX_POWER_MODE_ALTERNATE'           : 0x02,\
    'EMBER_TX_POWER_MODE_BOOST_AND_ALTERNATE' : 0x03,\
}
ember_config_tx_power_mode_rev = {}
for mode,num in ember_config_tx_power_mode.items():
    ember_config_tx_power_mode_rev[num] = mode


# EzspPolicyId
EZSP_TRUST_CENTER_POLICY                = 0x00
EZSP_BINDING_MODIFICATION_POLICY        = 0x01
EZSP_UNICAST_REPLIES_POLICY             = 0x02
EZSP_POLL_HANDLER_POLICY                = 0x03
EZSP_MESSAGE_CONTENTS_IN_CALLBACK_POLICY = 0x04
EZSP_TC_KEY_REQUEST_POLICY              = 0x05
EZSP_APP_KEY_REQUEST_POLICY             = 0x06
ezsp_policy_id = {\
    'EZSP_TRUST_CENTER_POLICY'                : 0x00,\
    'EZSP_BINDING_MODIFICATION_POLICY'        : 0x01,\
    'EZSP_UNICAST_REPLIES_POLICY'             : 0x02,\
    'EZSP_POLL_HANDLER_POLICY'                : 0x03,\
    'EZSP_MESSAGE_CONTENTS_IN_CALLBACK_POLICY' : 0x04,\
    'EZSP_TC_KEY_REQUEST_POLICY'              : 0x05,\
    'EZSP_APP_KEY_REQUEST_POLICY'             : 0x06,\
}
ezsp_policy_id_rev = {}
for pid,num in ezsp_policy_id.items():
    ezsp_policy_id_rev[num] = pid


# EzspDecisionid
EZSP_ALLOW_JOINS                        = 0x00
EZSP_ALLOW_JOINS_REJOINS_HAVE_LINK_KEY  = 0x04
EZSP_ALLOW_PRECONFIGURED_KEY_JOINS      = 0x01
EZSP_ALLOW_REJOINS_ONLY                 = 0x02
EZSP_DISALLOW_ALL_JOINS_AND_REJOINS     = 0x03
EZSP_DISALLOW_BINDING_MODIFICATION      = 0x10
EZSP_ALLOW_BINDING_MODIFICATION         = 0x11
EZSP_HOST_WILL_NOT_SUPPLY_REPLY         = 0x20
EZSP_HOST_WILL_SUPPLY_REPLY             = 0x21
EZSP_POLL_HANDLER_IGNORE                = 0x30
EZSP_POLL_HANDLER_CALLBACK              = 0x31
EZSP_MESSAGE_TAG_ONLY_IN_CALLBACK       = 0x40
EZSP_MESSAGE_TAG_AND_CONTENTS_IN_CALLBACK = 0x41
EZSP_DENY_TC_KEY_REQUESTS               = 0x50
EZSP_ALLOW_TC_KEY_REQUESTS              = 0x51
EZSP_DENY_APP_KEY_REQUESTS              = 0x60
EZSP_ALLOW_APP_KEY_REQUESTS             = 0x61
ezsp_decision_id = {
    'EZSP_ALLOW_JOINS'                        : 0x00,\
    'EZSP_ALLOW_JOINS_REJOINS_HAVE_LINK_KEY'  : 0x04,\
    'EZSP_ALLOW_PRECONFIGURED_KEY_JOINS'      : 0x01,\
    'EZSP_ALLOW_REJOINS_ONLY'                 : 0x02,\
    'EZSP_DISALLOW_ALL_JOINS_AND_REJOINS'     : 0x03,\
    'EZSP_DISALLOW_BINDING_MODIFICATION'      : 0x10,\
    'EZSP_ALLOW_BINDING_MODIFICATION'         : 0x11,\
    'EZSP_HOST_WILL_NOT_SUPPLY_REPLY'         : 0x20,\
    'EZSP_HOST_WILL_SUPPLY_REPLY'             : 0x21,\
    'EZSP_POLL_HANDLER_IGNORE'                : 0x30,\
    'EZSP_POLL_HANDLER_CALLBACK'              : 0x31,\
    'EZSP_MESSAGE_TAG_ONLY_IN_CALLBACK'       : 0x40,\
    'EZSP_MESSAGE_TAG_AND_CONTENTS_IN_CALLBACK' : 0x41,\
    'EZSP_DENY_TC_KEY_REQUESTS'               : 0x50,\
    'EZSP_ALLOW_TC_KEY_REQUESTS'              : 0x51,\
    'EZSP_DENY_APP_KEY_REQUESTS'              : 0x60,\
    'EZSP_ALLOW_APP_KEY_REQUESTS'             : 0x61,\
}
ezsp_decision_id_rev = {}
for did,num in ezsp_decision_id.items():
    ezsp_decision_id_rev[num] = did


# EzspMfgTokenId
EZSP_MFG_CUSTOM_VERSION                 = 0x00
EZSP_MFG_STRING                         = 0x01
EZSP_MFG_BOARD_NAME                     = 0x02
EZSP_MFG_MANUF_ID                       = 0x03
EZSP_MFG_PHY_CONFIG                     = 0x04
EZSP_MFG_BOOTLOAD_AES_KEY               = 0x05
EZSP_MFG_ASH_CONFIG                     = 0x06
EZSP_MFG_EZSP_STORAGE                   = 0x07
EZSP_STACK_CAL_DATA                     = 0x08
EZSP_MFG_CBKE_DATA                      = 0x09
EZSP_MFG_INSTALLATION_CODE              = 0x0A
ezsp_mfg_token_id = {
    'EZSP_MFG_CUSTOM_VERSION'                 : 0x00,\
    'EZSP_MFG_STRING'                         : 0x01,\
    'EZSP_MFG_BOARD_NAME'                     : 0x02,\
    'EZSP_MFG_MANUF_ID'                       : 0x03,\
    'EZSP_MFG_PHY_CONFIG'                     : 0x04,\
    'EZSP_MFG_BOOTLOAD_AES_KEY'               : 0x05,\
    'EZSP_MFG_ASH_CONFIG'                     : 0x06,\
    'EZSP_MFG_EZSP_STORAGE'                   : 0x07,\
    'EZSP_STACK_CAL_DATA'                     : 0x08,\
    'EZSP_MFG_CBKE_DATA'                      : 0x09,\
    'EZSP_MFG_INSTALLATION_CODE'              : 0x0A,\
}
ezsp_mfg_token_id_rev = {}
for tid,num in ezsp_mfg_token_id.items():
    ezsp_mfg_token_id_rev[num] = tid


# EzspStatus
EZSP_SUCCESS                            = 0x00
EZSP_SPI_ERR_FATAL                      = 0x10
EZSP_SPI_ERR_EM260_RESET                = 0x11
EZSP_SPI_ERR_OVERSIZED_EZSP_FRAME       = 0x12
EZSP_SPI_ERR_ABORTED_TRANSACTION        = 0x13
EZSP_SPI_ERR_MISSING_FRAME_TERMINATOR   = 0x14
EZSP_SPI_ERR_WAIT_SECTION_TIMEOUT       = 0x15
EZSP_SPI_ERR_NO_FRAME_TERMINATOR        = 0x16
EZSP_SPI_ERR_EZSP_COMMAND_OVERSIZED     = 0x17
EZSP_SPI_ERR_EZSP_RESPONSE_OVERSIZED    = 0x18
EZSP_SPI_WAITING_FOR_RESPONSE           = 0x19
EZSP_SPI_ERR_HANDSHAKE_TIMEOUT          = 0x1A
EZSP_SPI_ERR_STARTUP_TIMEOUT            = 0x1B
EZSP_SPI_ERR_STARTUP_FAIL               = 0x1C
EZSP_SPI_ERR_UNSUPPORTED_SPI_COMMAND    = 0x1D
EZSP_ASH_IN_PROGRESS                    = 0x20
EZSP_ASH_HOST_FATAL_ERROR               = 0x21
EZSP_ASH_NCP_FATAL_ERROR                = 0x22
EZSP_ASH_DATA_FRAME_TOO_LONG            = 0x23
EZSP_ASH_DATA_FRAME_TOO_SHORT           = 0x24
EZSP_ASH_NO_TX_SPACE                    = 0x25
EZSP_ASH_NO_RX_SPACE                    = 0x26
EZSP_ASH_NO_RX_DATA                     = 0x27
EZSP_ASH_NOT_CONNECTED                  = 0x28
EZSP_ERROR_VERSION_NOT_SET              = 0x30
EZSP_ERROR_INVALID_FRAME_ID             = 0x31
EZSP_ERROR_WRONG_DIRECTION              = 0x32
EZSP_ERROR_TRUNCATED                    = 0x33
EZSP_ERROR_OVERFLOW                     = 0x34
EZSP_ERROR_OUT_OF_MEMORY                = 0x35
EZSP_ERROR_INVALID_VALUE                = 0x36
EZSP_ERROR_INVALID_ID                   = 0x37
EZSP_ERROR_INVALID_CALL                 = 0x38
EZSP_ERROR_NO_RESPONSE                  = 0x39
EZSP_ERROR_COMMAND_TOO_LONG             = 0x40
EZSP_ERROR_QUEUE_FULL                   = 0x41
EZSP_ASH_ERROR_VERSION                  = 0x50
EZSP_ASH_ERROR_TIMEOUTS                 = 0x51
EZSP_ASH_ERROR_RESET_FAIL               = 0x52
EZSP_ASH_ERROR_NCP_RESET                = 0x53
EZSP_ASH_ERROR_SERIAL_INIT              = 0x54
EZSP_ASH_ERROR_NCP_TYPE                 = 0x55
EZSP_ASH_ERROR_RESET_METHOD             = 0x56
EZSP_ASH_ERROR_XON_XOFF                 = 0x57
EZSP_ASH_STARTED                        = 0x70
EZSP_ASH_CONNECTED                      = 0x71
EZSP_ASH_DISCONNECTED                   = 0x72
EZSP_ASH_ACK_TIMEOUT                    = 0x73
EZSP_ASH_CANCELLED                      = 0x74
EZSP_ASH_OUT_OF_SEQUENCE                = 0x75
EZSP_ASH_BAD_CRC                        = 0x76
EZSP_ASH_COMM_ERROR                     = 0x77
EZSP_ASH_BAD_ACKNUM                     = 0x78
EZSP_ASH_TOO_SHORT                      = 0x79
EZSP_ASH_TOO_LONG                       = 0x7A
EZSP_ASH_BAD_CONTROL                    = 0x7B
EZSP_ASH_BAD_LENGTH                     = 0x7C
EZSP_ASH_NO_ERROR                       = 0xFF
ezsp_status = {\
    'EZSP_SUCCESS'                            : 0x00,\
    'EZSP_SPI_ERR_FATAL'                      : 0x10,\
    'EZSP_SPI_ERR_EM260_RESET'                : 0x11,\
    'EZSP_SPI_ERR_OVERSIZED_EZSP_FRAME'       : 0x12,\
    'EZSP_SPI_ERR_ABORTED_TRANSACTION'        : 0x13,\
    'EZSP_SPI_ERR_MISSING_FRAME_TERMINATOR'   : 0x14,\
    'EZSP_SPI_ERR_WAIT_SECTION_TIMEOUT'       : 0x15,\
    'EZSP_SPI_ERR_NO_FRAME_TERMINATOR'        : 0x16,\
    'EZSP_SPI_ERR_EZSP_COMMAND_OVERSIZED'     : 0x17,\
    'EZSP_SPI_ERR_EZSP_RESPONSE_OVERSIZED'    : 0x18,\
    'EZSP_SPI_WAITING_FOR_RESPONSE'           : 0x19,\
    'EZSP_SPI_ERR_HANDSHAKE_TIMEOUT'          : 0x1A,\
    'EZSP_SPI_ERR_STARTUP_TIMEOUT'            : 0x1B,\
    'EZSP_SPI_ERR_STARTUP_FAIL'               : 0x1C,\
    'EZSP_SPI_ERR_UNSUPPORTED_SPI_COMMAND'    : 0x1D,\
    'EZSP_ASH_IN_PROGRESS'                    : 0x20,\
    'EZSP_ASH_HOST_FATAL_ERROR'               : 0x21,\
    'EZSP_ASH_NCP_FATAL_ERROR'                : 0x22,\
    'EZSP_ASH_DATA_FRAME_TOO_LONG'            : 0x23,\
    'EZSP_ASH_DATA_FRAME_TOO_SHORT'           : 0x24,\
    'EZSP_ASH_NO_TX_SPACE'                    : 0x25,\
    'EZSP_ASH_NO_RX_SPACE'                    : 0x26,\
    'EZSP_ASH_NO_RX_DATA'                     : 0x27,\
    'EZSP_ASH_NOT_CONNECTED'                  : 0x28,\
    'EZSP_ERROR_VERSION_NOT_SET'              : 0x30,\
    'EZSP_ERROR_INVALID_FRAME_ID'             : 0x31,\
    'EZSP_ERROR_WRONG_DIRECTION'              : 0x32,\
    'EZSP_ERROR_TRUNCATED'                    : 0x33,\
    'EZSP_ERROR_OVERFLOW'                     : 0x34,\
    'EZSP_ERROR_OUT_OF_MEMORY'                : 0x35,\
    'EZSP_ERROR_INVALID_VALUE'                : 0x36,\
    'EZSP_ERROR_INVALID_ID'                   : 0x37,\
    'EZSP_ERROR_INVALID_CALL'                 : 0x38,\
    'EZSP_ERROR_NO_RESPONSE'                  : 0x39,\
    'EZSP_ERROR_COMMAND_TOO_LONG'             : 0x40,\
    'EZSP_ERROR_QUEUE_FULL'                   : 0x41,\
    'EZSP_ASH_ERROR_VERSION'                  : 0x50,\
    'EZSP_ASH_ERROR_TIMEOUTS'                 : 0x51,\
    'EZSP_ASH_ERROR_RESET_FAIL'               : 0x52,\
    'EZSP_ASH_ERROR_NCP_RESET'                : 0x53,\
    'EZSP_ASH_ERROR_SERIAL_INIT'              : 0x54,\
    'EZSP_ASH_ERROR_NCP_TYPE'                 : 0x55,\
    'EZSP_ASH_ERROR_RESET_METHOD'             : 0x56,\
    'EZSP_ASH_ERROR_XON_XOFF'                 : 0x57,\
    'EZSP_ASH_STARTED'                        : 0x70,\
    'EZSP_ASH_CONNECTED'                      : 0x71,\
    'EZSP_ASH_DISCONNECTED'                   : 0x72,\
    'EZSP_ASH_ACK_TIMEOUT'                    : 0x73,\
    'EZSP_ASH_CANCELLED'                      : 0x74,\
    'EZSP_ASH_OUT_OF_SEQUENCE'                : 0x75,\
    'EZSP_ASH_BAD_CRC'                        : 0x76,\
    'EZSP_ASH_COMM_ERROR'                     : 0x77,\
    'EZSP_ASH_BAD_ACKNUM'                     : 0x78,\
    'EZSP_ASH_TOO_SHORT'                      : 0x79,\
    'EZSP_ASH_TOO_LONG'                       : 0x7A,\
    'EZSP_ASH_BAD_CONTROL'                    : 0x7B,\
    'EZSP_ASH_BAD_LENGTH'                     : 0x7C,\
    'EZSP_ASH_NO_ERROR'                       : 0xFF,\
}
ezsp_status_rev = {}
for tid,num in ezsp_status.items():
    ezsp_status_rev[num] = tid


# EmberStatus
EMBER_SUCCESS                           = 0x00
EMBER_ERR_FATAL                         = 0x01
EMBER_EEPROM_MFG_STACK_VERSION_MISMATCH = 0x04
EMBER_INCOMPATIBLE_STATIC_MEMORY_DEFINITIONS = 0x05
EMBER_EEPROM_MFG_VERSION_MISMATCH       = 0x06
EMBER_EEPROM_STACK_VERSION_MISMATCH     = 0x07
EMBER_NO_BUFFERS                        = 0x18
EMBER_SERIAL_INVALID_BAUD_RATE          = 0x20
EMBER_SERIAL_INVALID_PORT               = 0x21
EMBER_SERIAL_TX_OVERFLOW                = 0x22
EMBER_SERIAL_RX_OVERFLOW                = 0x23
EMBER_SERIAL_RX_FRAME_ERROR             = 0x24
EMBER_SERIAL_RX_PARITY_ERROR            = 0x25
EMBER_SERIAL_RX_EMPTY                   = 0x26
EMBER_SERIAL_RX_OVERRUN_ERROR           = 0x27
EMBER_MAC_TRANSMIT_QUEUE_FULL           = 0x39
EMBER_MAC_UNKNOWN_HEADER_TYPE           = 0x3A
EMBER_MAC_SCANNING                      = 0x3D
EMBER_MAC_NO_DATA                       = 0x31
EMBER_MAC_JOINED_NETWORK                = 0x32
EMBER_MAC_BAD_SCAN_DURATION             = 0x33
EMBER_MAC_INCORRECT_SCAN_TYPE           = 0x34
EMBER_MAC_INVALID_CHANNEL_MASK          = 0x35
EMBER_MAC_COMMAND_TRANSMIT_FAILURE      = 0x36
EMBER_MAC_NO_ACK_RECEIVED               = 0x40
EMBER_MAC_INDIRECT_TIMEOUT              = 0x42
EMBER_SIM_EEPROM_ERASE_PAGE_GREEN       = 0x43
EMBER_SIM_EEPROM_ERASE_PAGE_RED         = 0x44
EMBER_SIM_EEPROM_FULL                   = 0x45
EMBER_ERR_FLASH_WRITE_INHIBITED         = 0x46
EMBER_ERR_FLASH_VERIFY_FAILED           = 0x47
EMBER_SIM_EEPROM_INIT_1_FAILED          = 0x48
EMBER_SIM_EEPROM_INIT_2_FAILED          = 0x49
EMBER_SIM_EEPROM_INIT_3_FAILED          = 0x4A
EMBER_ERR_TOKEN_UNKNOWN                 = 0x4B
EMBER_ERR_TOKEN_EXISTS                  = 0x4C
EMBER_ERR_TOKEN_INVALID_SIZE            = 0x4D
EMBER_ERR_TOKEN_READ_ONLY               = 0x4E
EMBER_ERR_BOOTLOADER_TRAP_TABLE_BAD     = 0x58
EMBER_ERR_BOOTLOADER_TRAP_UNKNOWN       = 0x59
EMBER_ERR_BOOTLOADER_NO_IMAGE           = 0x5A
EMBER_DELIVERY_FAILED                   = 0x66
EMBER_BINDING_INDEX_OUT_OF_RANGE        = 0x69
EMBER_ADDRESS_TABLE_INDEX_OUT_OF_RANGE  = 0x6A
EMBER_INVALID_BINDING_INDEX             = 0x6C
EMBER_INVALID_CALL                      = 0x70
EMBER_COST_NOT_KNOWN                    = 0x71
EMBER_MAX_MESSAGE_LIMIT_REACHED         = 0x72
EMBER_MESSAGE_TOO_LONG                  = 0x74
EMBER_BINDING_IS_ACTIVE                 = 0x75
EMBER_ADDRESS_TABLE_ENTRY_IS_ACTIVE     = 0x76
EMBER_ADC_CONVERSION_DONE               = 0x80
EMBER_ADC_CONVERSION_BUSY               = 0x81
EMBER_ADC_CONVERSION_DEFERRED           = 0x82
EMBER_ADC_NO_CONVERSION_PENDING         = 0x84
EMBER_SLEEP_INTERRUPTED                 = 0x85
EMBER_PHY_TX_UNDERFLOW                  = 0x88
EMBER_PHY_TX_INCOMPLETE                 = 0x89
EMBER_PHY_INVALID_CHANNEL               = 0x8A
EMBER_PHY_INVALID_POWER                 = 0x8B
EMBER_PHY_TX_BUSY                       = 0x8C
EMBER_PHY_UNKNOWN_RADIO_TYPE            = 0x8D
EMBER_PHY_OSCILLATOR_CHECK_FAILED       = 0x8E
EMBER_PHY_PARTIAL_PACKET                = 0x8F
EMBER_NETWORK_UP                        = 0x90
EMBER_NETWORK_DOWN                      = 0x91
EMBER_JOIN_FAILED                       = 0x94
EMBER_MOVE_FAILED                       = 0x96
EMBER_CANNOT_JOIN_AS_ROUTER             = 0x98
EMBER_NODE_ID_CHANGED                   = 0x99
EMBER_PAN_ID_CHANGED                    = 0x9A
EMBER_NO_BEACONS                        = 0xAB
EMBER_RECEIVED_KEY_IN_THE_CLEAR         = 0xAC
EMBER_NO_NETWORK_KEY_RECEIVED           = 0xAD
EMBER_NO_LINK_KEY_RECEIVED              = 0xAE
EMBER_PRECONFIGURED_KEY_REQUIRED        = 0xAF
EMBER_NOT_JOINED                        = 0x93
EMBER_INVALID_SECURITY_LEVEL            = 0x95
EMBER_NETWORK_BUSY                      = 0xA1
EMBER_INVALID_ENDPOINT                  = 0xA3
EMBER_BINDING_HAS_CHANGED               = 0xA4
EMBER_INSUFFICIENT_RANDOM_DATA          = 0xA5
EMBER_APS_ENCRYPTION_ERROR              = 0xA6
EMBER_TRUST_CENTER_MASTER_KEY_NOT_SET   = 0xA7
EMBER_SECURITY_STATE_NOT_SET            = 0xA8
EMBER_KEY_TABLE_INVALID_ADDRESS         = 0xB3
EMBER_SECURITY_CONFIGURATION_INVALID    = 0xB7
EMBER_TOO_SOON_FOR_SWITCH_KEY           = 0xB8
EMBER_KEY_NOT_AUTHORIZED                = 0xBB
EMBER_SOURCE_ROUTE_FAILURE              = 0xA9
EMBER_MANY_TO_ONE_ROUTE_FAILURE         = 0xAA
EMBER_STACK_AND_HARDWARE_MISMATCH       = 0xB0
EMBER_APPLICATION_ERROR_0               = 0xF0
EMBER_APPLICATION_ERROR_1               = 0xF1
EMBER_APPLICATION_ERROR_2               = 0xF2
EMBER_APPLICATION_ERROR_3               = 0xF3
EMBER_APPLICATION_ERROR_4               = 0xF4
EMBER_APPLICATION_ERROR_5               = 0xF5
EMBER_APPLICATION_ERROR_6               = 0xF6
EMBER_APPLICATION_ERROR_7               = 0xF7
EMBER_APPLICATION_ERROR_8               = 0xF8
EMBER_APPLICATION_ERROR_9               = 0xF9
EMBER_APPLICATION_ERROR_10              = 0xFA
EMBER_APPLICATION_ERROR_11              = 0xFB
EMBER_APPLICATION_ERROR_12              = 0xFC
EMBER_APPLICATION_ERROR_13              = 0xFD
EMBER_APPLICATION_ERROR_14              = 0xFE
EMBER_APPLICATION_ERROR_15              = 0xFF
ember_status = {\
    'EMBER_SUCCESS'                           : 0x00,\
    'EMBER_ERR_FATAL'                         : 0x01,\
    'EMBER_EEPROM_MFG_STACK_VERSION_MISMATCH' : 0x04,\
    'EMBER_INCOMPATIBLE_STATIC_MEMORY_DEFINITIONS' : 0x05,\
    'EMBER_EEPROM_MFG_VERSION_MISMATCH'       : 0x06,\
    'EMBER_EEPROM_STACK_VERSION_MISMATCH'     : 0x07,\
    'EMBER_NO_BUFFERS'                        : 0x18,\
    'EMBER_SERIAL_INVALID_BAUD_RATE'          : 0x20,\
    'EMBER_SERIAL_INVALID_PORT'               : 0x21,\
    'EMBER_SERIAL_TX_OVERFLOW'                : 0x22,\
    'EMBER_SERIAL_RX_OVERFLOW'                : 0x23,\
    'EMBER_SERIAL_RX_FRAME_ERROR'             : 0x24,\
    'EMBER_SERIAL_RX_PARITY_ERROR'            : 0x25,\
    'EMBER_SERIAL_RX_EMPTY'                   : 0x26,\
    'EMBER_SERIAL_RX_OVERRUN_ERROR'           : 0x27,\
    'EMBER_MAC_TRANSMIT_QUEUE_FULL'           : 0x39,\
    'EMBER_MAC_UNKNOWN_HEADER_TYPE'           : 0x3A,\
    'EMBER_MAC_SCANNING'                      : 0x3D,\
    'EMBER_MAC_NO_DATA'                       : 0x31,\
    'EMBER_MAC_JOINED_NETWORK'                : 0x32,\
    'EMBER_MAC_BAD_SCAN_DURATION'             : 0x33,\
    'EMBER_MAC_INCORRECT_SCAN_TYPE'           : 0x34,\
    'EMBER_MAC_INVALID_CHANNEL_MASK'          : 0x35,\
    'EMBER_MAC_COMMAND_TRANSMIT_FAILURE'      : 0x36,\
    'EMBER_MAC_NO_ACK_RECEIVED'               : 0x40,\
    'EMBER_MAC_INDIRECT_TIMEOUT'              : 0x42,\
    'EMBER_SIM_EEPROM_ERASE_PAGE_GREEN'       : 0x43,\
    'EMBER_SIM_EEPROM_ERASE_PAGE_RED'         : 0x44,\
    'EMBER_SIM_EEPROM_FULL'                   : 0x45,\
    'EMBER_ERR_FLASH_WRITE_INHIBITED'         : 0x46,\
    'EMBER_ERR_FLASH_VERIFY_FAILED'           : 0x47,\
    EMBER_SIM_EEPROM_INIT_1_FAILED          : 0x48,\
    EMBER_SIM_EEPROM_INIT_2_FAILED          : 0x49,\
    EMBER_SIM_EEPROM_INIT_3_FAILED          : 0x4A,\
    'EMBER_ERR_TOKEN_UNKNOWN'                 : 0x4B,\
    'EMBER_ERR_TOKEN_EXISTS'                  : 0x4C,\
    'EMBER_ERR_TOKEN_INVALID_SIZE'            : 0x4D,\
    'EMBER_ERR_TOKEN_READ_ONLY'               : 0x4E,\
    'EMBER_ERR_BOOTLOADER_TRAP_TABLE_BAD'     : 0x58,\
    'EMBER_ERR_BOOTLOADER_TRAP_UNKNOWN'       : 0x59,\
    'EMBER_ERR_BOOTLOADER_NO_IMAGE'           : 0x5A,\
    'EMBER_DELIVERY_FAILED'                   : 0x66,\
    'EMBER_BINDING_INDEX_OUT_OF_RANGE'        : 0x69,\
    'EMBER_ADDRESS_TABLE_INDEX_OUT_OF_RANGE'  : 0x6A,\
    'EMBER_INVALID_BINDING_INDEX'             : 0x6C,\
    'EMBER_INVALID_CALL'                      : 0x70,\
    'EMBER_COST_NOT_KNOWN'                    : 0x71,\
    'EMBER_MAX_MESSAGE_LIMIT_REACHED'         : 0x72,\
    'EMBER_MESSAGE_TOO_LONG'                  : 0x74,\
    'EMBER_BINDING_IS_ACTIVE'                 : 0x75,\
    'EMBER_ADDRESS_TABLE_ENTRY_IS_ACTIVE'     : 0x76,\
    'EMBER_ADC_CONVERSION_DONE'               : 0x80,\
    'EMBER_ADC_CONVERSION_BUSY'               : 0x81,\
    'EMBER_ADC_CONVERSION_DEFERRED'           : 0x82,\
    'EMBER_ADC_NO_CONVERSION_PENDING'         : 0x84,\
    'EMBER_SLEEP_INTERRUPTED'                 : 0x85,\
    'EMBER_PHY_TX_UNDERFLOW'                  : 0x88,\
    'EMBER_PHY_TX_INCOMPLETE'                 : 0x89,\
    'EMBER_PHY_INVALID_CHANNEL'               : 0x8A,\
    'EMBER_PHY_INVALID_POWER'                 : 0x8B,\
    'EMBER_PHY_TX_BUSY'                       : 0x8C,\
    'EMBER_PHY_UNKNOWN_RADIO_TYPE'            : 0x8D,\
    'EMBER_PHY_OSCILLATOR_CHECK_FAILED'       : 0x8E,\
    'EMBER_PHY_PARTIAL_PACKET'                : 0x8F,\
    'EMBER_NETWORK_UP'                        : 0x90,\
    'EMBER_NETWORK_DOWN'                      : 0x91,\
    'EMBER_JOIN_FAILED'                       : 0x94,\
    'EMBER_MOVE_FAILED'                       : 0x96,\
    'EMBER_CANNOT_JOIN_AS_ROUTER'             : 0x98,\
    'EMBER_NODE_ID_CHANGED'                   : 0x99,\
    'EMBER_PAN_ID_CHANGED'                    : 0x9A,\
    'EMBER_NO_BEACONS'                        : 0xAB,\
    'EMBER_RECEIVED_KEY_IN_THE_CLEAR'         : 0xAC,\
    'EMBER_NO_NETWORK_KEY_RECEIVED'           : 0xAD,\
    'EMBER_NO_LINK_KEY_RECEIVED'              : 0xAE,\
    'EMBER_PRECONFIGURED_KEY_REQUIRED'        : 0xAF,\
    'EMBER_NOT_JOINED'                        : 0x93,\
    'EMBER_INVALID_SECURITY_LEVEL'            : 0x95,\
    'EMBER_NETWORK_BUSY'                      : 0xA1,\
    'EMBER_INVALID_ENDPOINT'                  : 0xA3,\
    'EMBER_BINDING_HAS_CHANGED'               : 0xA4,\
    'EMBER_INSUFFICIENT_RANDOM_DATA'          : 0xA5,\
    'EMBER_APS_ENCRYPTION_ERROR'              : 0xA6,\
    'EMBER_TRUST_CENTER_MASTER_KEY_NOT_SET'   : 0xA7,\
    'EMBER_SECURITY_STATE_NOT_SET'            : 0xA8,\
    'EMBER_KEY_TABLE_INVALID_ADDRESS'         : 0xB3,\
    'EMBER_SECURITY_CONFIGURATION_INVALID'    : 0xB7,\
    'EMBER_TOO_SOON_FOR_SWITCH_KEY'           : 0xB8,\
    'EMBER_KEY_NOT_AUTHORIZED'                : 0xBB,\
    'EMBER_SOURCE_ROUTE_FAILURE'              : 0xA9,\
    'EMBER_MANY_TO_ONE_ROUTE_FAILURE'         : 0xAA,\
    'EMBER_STACK_AND_HARDWARE_MISMATCH'       : 0xB0,\
    'EMBER_APPLICATION_ERROR_0'               : 0xF0,\
    'EMBER_APPLICATION_ERROR_1'               : 0xF1,\
    'EMBER_APPLICATION_ERROR_2'               : 0xF2,\
    'EMBER_APPLICATION_ERROR_3'               : 0xF3,\
    'EMBER_APPLICATION_ERROR_4'               : 0xF4,\
    'EMBER_APPLICATION_ERROR_5'               : 0xF5,\
    'EMBER_APPLICATION_ERROR_6'               : 0xF6,\
    'EMBER_APPLICATION_ERROR_7'               : 0xF7,\
    'EMBER_APPLICATION_ERROR_8'               : 0xF8,\
    'EMBER_APPLICATION_ERROR_9'               : 0xF9,\
    'EMBER_APPLICATION_ERROR_10'              : 0xFA,\
    'EMBER_APPLICATION_ERROR_11'              : 0xFB,\
    'EMBER_APPLICATION_ERROR_12'              : 0xFC,\
    'EMBER_APPLICATION_ERROR_13'              : 0xFD,\
    'EMBER_APPLICATION_ERROR_14'              : 0xFE,\
    'EMBER_APPLICATION_ERROR_15'              : 0xFF,\
}
ember_status_rev = {}
for tid,num in ember_status.items():
    ember_status_rev[num] = tid


# EmberEventUnits
EMBER_EVENT_INACTIVE                    = 0x00
EMBER_EVENT_MS_TIME                     = 0x01
EMBER_EVENT_QS_TIME                     = 0x02
EMBER_EVENT_MINUTE_TIME                 = 0x03
ember_event_units = {\
    'EMBER_EVENT_INACTIVE'                    : 0x00,\
    'EMBER_EVENT_MS_TIME'                     : 0x01,\
    'EMBER_EVENT_QS_TIME'                     : 0x02,\
    'EMBER_EVENT_MINUTE_TIME'                 : 0x03,\
}
ember_event_units_rev = {}
for tid,num in ember_event_units.items():
    ember_event_units_rev[num] = tid


# EmberNodeType
EMBER_UNKNOWN_DEVICE                    = 0x00
EMBER_COORDINATOR                       = 0x01
EMBER_ROUTER                            = 0x02
EMBER_END_DEVICE                        = 0x03
EMBER_SLEEPY_END_DEVICE                 = 0x04
EMBER_MOBILE_END_DEVICE                 = 0x05 
ember_node_type = {\
    'EMBER_UNKNOWN_DEVICE'                    : 0x00,\
    'EMBER_COORDINATOR'                       : 0x01,\
    'EMBER_ROUTER'                            : 0x02,\
    'EMBER_END_DEVICE'                        : 0x03,\
    'EMBER_SLEEPY_END_DEVICE'                 : 0x04,\
    'EMBER_MOBILE_END_DEVICE'                 : 0x05 ,\
}
ember_node_type_rev = {}
for tid,num in ember_node_type.items():
    ember_node_type_rev[num] = tid


# EmberNetworkStatus
EMBER_NO_NETWORK                        = 0x00
EMBER_JOINING_NETWORK                   = 0x01
EMBER_JOINED_NETWORK                    = 0x02
EMBER_JOINED_NETWORK_NO_PARENT          = 0x03
EMBER_LEAVING_NETWORK                   = 0x04 
ember_network_status = {\
    'EMBER_NO_NETWORK'                        : 0x00,\
    'EMBER_JOINING_NETWORK'                   : 0x01,\
    'EMBER_JOINED_NETWORK'                    : 0x02,\
    'EMBER_JOINED_NETWORK_NO_PARENT'          : 0x03,\
    'EMBER_LEAVING_NETWORK'                   : 0x04 ,\
}
ember_network_status_rev = {}
for tid,num in ember_network_status.items():
    ember_network_status_rev[num] = tid


# EmberIncomingMessageType
EMBER_INCOMING_UNICAST                  = 0x00
EMBER_INCOMING_UNICAST_REPLY            = 0x01
EMBER_INCOMING_MULTICAST                = 0x02
EMBER_INCOMING_MULTICAST_LOOPBACK       = 0x03
EMBER_INCOMING_BROADCAST                = 0x04
EMBER_INCOMING_BROADCAST_LOOPBACK       = 0x05
EMBER_INCOMING_MANY_TO_ONE_ROUTE_REQUEST = 0x06
ember_incoming_message_type = {\
    'EMBER_INCOMING_UNICAST'                  : 0x00,\
    'EMBER_INCOMING_UNICAST_REPLY'            : 0x01,\
    'EMBER_INCOMING_MULTICAST'                : 0x02,\
    'EMBER_INCOMING_MULTICAST_LOOPBACK'       : 0x03,\
    'EMBER_INCOMING_BROADCAST'                : 0x04,\
    'EMBER_INCOMING_BROADCAST_LOOPBACK'       : 0x05,\
    'EMBER_INCOMING_MANY_TO_ONE_ROUTE_REQUEST' : 0x06,\
}
ember_incoming_message_type_rev = {}
for tid,num in ember_incoming_message_type.items():
    ember_incoming_message_type_rev[num] = tid


# EmberOutgoingMessageType
EMBER_OUTGOING_DIRECT                   = 0x00
EMBER_OUTGOING_VIA_ADDRESS_TABLE        = 0x01
EMBER_OUTGOING_VIA_BINDING              = 0x02
EMBER_OUTGOING_MULTICAST                = 0x03
EMBER_OUTGOING_BROADCAST                = 0x04
ember_outgoing_message_type = {\
    'EMBER_OUTGOING_DIRECT'                   : 0x00,\
    'EMBER_OUTGOING_VIA_ADDRESS_TABLE'        : 0x01,\
    'EMBER_OUTGOING_VIA_BINDING'              : 0x02,\
    'EMBER_OUTGOING_MULTICAST'                : 0x03,\
    'EMBER_OUTGOING_BROADCAST'                : 0x04,\
}
ember_outgoing_message_type_rev = {}
for tid,num in ember_outgoing_message_type.items():
    ember_outgoing_message_type_rev[num] = tid


# EmberMacPassthroughType
EMBER_MAC_PASSTHROUGH_NONE              = 0x00
EMBER_MAC_PASSTHROUGH_SE_INTERPAN       = 0x01
EMBER_MAC_PASSTHROUGH_EMBERNET          = 0x02
EMBER_MAC_PASSTHROUGH_EMBERNET_SOURCE   = 0x04
ember_mac_passthrough_type = {\
    'EMBER_MAC_PASSTHROUGH_NONE'              : 0x00,\
    'EMBER_MAC_PASSTHROUGH_SE_INTERPAN'       : 0x01,\
    'EMBER_MAC_PASSTHROUGH_EMBERNET'          : 0x02,\
    'EMBER_MAC_PASSTHROUGH_EMBERNET_SOURCE'   : 0x04,\
}
ember_mac_passthrough_type_rev = {}
for tid,num in ember_mac_passthrough_type.items():
    ember_mac_passthrough_type_rev[num] = tid


# EmberBindingType
EMBER_UNUSED_BINDING                    = 0x00
EMBER_UNICAST_BINDING                   = 0x01
EMBER_MANY_TO_ONE_BINDING               = 0x02
EMBER_MULTICAST_BINDING                 = 0x03
ember_binding_type = {\
    'EMBER_UNUSED_BINDING'                    : 0x00,\
    'EMBER_UNICAST_BINDING'                   : 0x01,\
    'EMBER_MANY_TO_ONE_BINDING'               : 0x02,\
    'EMBER_MULTICAST_BINDING'                 : 0x03,\
}
ember_binding_type_rev = {}
for tid,num in ember_binding_type.items():
    ember_binding_type_rev[num] = tid


# EmberApsOption
EMBER_APS_OPTION_NONE                   = 0x0000
EMBER_APS_OPTION_ENCRYPTION             = 0x0020
EMBER_APS_OPTION_RETRY                  = 0x0040
EMBER_APS_OPTION_ENABLE_ROUTE_DISCOVERY = 0x0100
EMBER_APS_OPTION_FORCE_ROUTE_DISCOVERY  = 0x0200
EMBER_APS_OPTION_SOURCE_EUI64           = 0x0400
EMBER_APS_OPTION_DESTINATION_EUI64      = 0x0800
EMBER_APS_OPTION_ENABLE_ADDRESS_DISCOVERY = 0x1000
EMBER_APS_OPTION_POLL_RESPONSE          = 0x2000
EMBER_APS_OPTION_FRAGMENT               = 0x8000
ember_aps_options = {\
    'EMBER_APS_OPTION_NONE'                   : 0x0000,\
    'EMBER_APS_OPTION_ENCRYPTION'             : 0x0020,\
    'EMBER_APS_OPTION_RETRY'                  : 0x0040,\
    'EMBER_APS_OPTION_ENABLE_ROUTE_DISCOVERY' : 0x0100,\
    'EMBER_APS_OPTION_FORCE_ROUTE_DISCOVERY'  : 0x0200,\
    'EMBER_APS_OPTION_SOURCE_EUI64'           : 0x0400,\
    'EMBER_APS_OPTION_DESTINATION_EUI64'      : 0x0800,\
    'EMBER_APS_OPTION_ENABLE_ADDRESS_DISCOVERY' : 0x1000,\
    'EMBER_APS_OPTION_POLL_RESPONSE'          : 0x2000,\
    'EMBER_APS_OPTION_FRAGMENT'               : 0x8000,\
}
ember_aps_options_rev = {}
for tid,num in ember_aps_options.items():
    ember_aps_options_rev[num] = tid


# EzspNetworkScanType
EZSP_ENERGY_SCAN                        = 0x00
EZSP_ACTIVE_SCAN                        = 0x01
EZSP_UNUSED_PAN_ID_SCAN                 = 0x02
EZSP_NEXT_JOINABLE_NETWORK_SCAN         = 0x03
ezsp_network_scan_type = {\
    'EZSP_ENERGY_SCAN'                        : 0x00,\
    'EZSP_ACTIVE_SCAN'                        : 0x01,\
    'EZSP_UNUSED_PAN_ID_SCAN'                 : 0x02,\
    'EZSP_NEXT_JOINABLE_NETWORK_SCAN'         : 0x03,\
}
ezsp_network_scan_type_rev = {}
for tid,num in ezsp_network_scan_type.items():
    ezsp_network_scan_type_rev[num] = tid


# EmberJoinDecision
EMBER_USE_PRECONFIGURED_KEY             = 0x00
EMBER_SEND_KEY_IN_THE_CLEAR             = 0x01
EMBER_DENY_JOIN                         = 0x02
EMBER_NO_ACTION                         = 0x03
ember_join_decision = {\
    'EMBER_USE_PRECONFIGURED_KEY'             : 0x00,\
    'EMBER_SEND_KEY_IN_THE_CLEAR'             : 0x01,\
    'EMBER_DENY_JOIN'                         : 0x02,\
    'EMBER_NO_ACTION'                         : 0x03,\
}
ember_join_decision_rev = {}
for tid,num in ember_join_decision.items():
    ember_join_decision_rev[num] = tid


# EmberInitialSecurityBitmask
EMBER_STANDARD_SECURITY_MODE            = 0x0000
EMBER_HIGH_SECURITY_MODE                = 0x0001
EMBER_DISTRIBUTED_TRUST_CENTER_MODE     = 0x0002
EMBER_GLOBAL_LINK_KEY                   = 0x0004
EMBER_PRECONFIGURED_NETWORK_KEY_MODE    = 0x0008
EMBER_TRUST_CENTER_USES_HASHED_LINK_KEY = 0x0084
EMBER_HAVE_PRECONFIGURED_KEY            = 0x0100
EMBER_HAVE_NETWORK_KEY                  = 0x0200
EMBER_GET_LINK_KEY_WHEN_JOINING         = 0x0400
EMBER_REQUIRE_ENCRYPTED_KEY             = 0x0800
ember_initial_security_bitmask = {\
    'EMBER_STANDARD_SECURITY_MODE'            : 0x0000,\
    'EMBER_HIGH_SECURITY_MODE'                : 0x0001,\
    'EMBER_DISTRIBUTED_TRUST_CENTER_MODE'     : 0x0002,\
    'EMBER_GLOBAL_LINK_KEY'                   : 0x0004,\
    'EMBER_PRECONFIGURED_NETWORK_KEY_MODE'    : 0x0008,\
    'EMBER_TRUST_CENTER_USES_HASHED_LINK_KEY' : 0x0084,\
    'EMBER_HAVE_PRECONFIGURED_KEY'            : 0x0100,\
    'EMBER_HAVE_NETWORK_KEY'                  : 0x0200,\
    'EMBER_GET_LINK_KEY_WHEN_JOINING'         : 0x0400,\
    'EMBER_REQUIRE_ENCRYPTED_KEY'             : 0x0800,\
}
ember_initial_security_bitmask_rev = {}
for tid,num in ember_initial_security_bitmask.items():
    ember_initial_security_bitmask_rev[num] = tid


# EmberCurrentSecurityBitmask
EMBER_STANDARD_SECURITY_MODE            = 0x0000
EMBER_HIGH_SECURITY_MODE                = 0x0001
EMBER_DISTRIBUTED_TRUST_CENTER_MODE     = 0x0002
EMBER_GLOBAL_LINK_KEY                   = 0x0004
EMBER_HAVE_TRUST_CENTER_LINK_KEY        = 0x0010
EMBER_TRUST_CENTER_USES_HASHED_LINK_KEY = 0x0084
ember_current_security_bitmask = {\
    'EMBER_STANDARD_SECURITY_MODE'            : 0x0000,\
    'EMBER_HIGH_SECURITY_MODE'                : 0x0001,\
    'EMBER_DISTRIBUTED_TRUST_CENTER_MODE'     : 0x0002,\
    'EMBER_GLOBAL_LINK_KEY'                   : 0x0004,\
    'EMBER_HAVE_TRUST_CENTER_LINK_KEY'        : 0x0010,\
    'EMBER_TRUST_CENTER_USES_HASHED_LINK_KEY' : 0x0084,\
}
ember_current_security_bitmask_rev = {}
for tid,num in ember_current_security_bitmask.items():
    ember_current_security_bitmask_rev[num] = tid


# EmberKeyType
EMBER_TRUST_CENTER_LINK_KEY             = 0x01
EMBER_TRUST_CENTER_MASTER_KEY           = 0x02
EMBER_CURRENT_NETWORK_KEY               = 0x03
EMBER_NEXT_NETWORK_KEY                  = 0x04
EMBER_APPLICATION_LINK_KEY              = 0x05
EMBER_APPLICATION_MASTER_KEY            = 0x06
ember_key_type = {\
    'EMBER_TRUST_CENTER_LINK_KEY'             : 0x01,\
    'EMBER_TRUST_CENTER_MASTER_KEY'           : 0x02,\
    'EMBER_CURRENT_NETWORK_KEY'               : 0x03,\
    'EMBER_NEXT_NETWORK_KEY'                  : 0x04,\
    'EMBER_APPLICATION_LINK_KEY'              : 0x05,\
    'EMBER_APPLICATION_MASTER_KEY'            : 0x06,\
}
ember_key_type_rev = {}
for tid,num in ember_key_type.items():
    ember_key_type_rev[num] = tid


# EmberKeyStructBitmask
EMBER_KEY_HAS_SEQUENCE_NUMBER           = 0x0001
EMBER_KEY_HAS_OUTGOING_FRAME_COUNTER    = 0x0002
EMBER_KEY_HAS_INCOMING_FRAME_COUNTER    = 0x0004
EMBER_KEY_HAS_PARTNER_EUI64             = 0x0008
ember_key_structure_bitmask = {\
    'EMBER_KEY_HAS_SEQUENCE_NUMBER'           : 0x0001,\
    'EMBER_KEY_HAS_OUTGOING_FRAME_COUNTER'    : 0x0002,\
    'EMBER_KEY_HAS_INCOMING_FRAME_COUNTER'    : 0x0004,\
    'EMBER_KEY_HAS_PARTNER_EUI64'             : 0x0008,\
}
ember_key_structure_bitmask_rev = {}
for tid,num in ember_key_structure_bitmask.items():
    ember_key_structure_bitmask_rev[num] = tid


# EmberDeviceUpdate
EMBER_STANDARD_SECURITY_SECURED_REJOIN  = 0x0
EMBER_STANDARD_SECURITY_UNSECURED_JOIN  = 0x1
EMBER_DEVICE_LEFT                       = 0x2
EMBER_STANDARD_SECURITY_UNSECURED_REJOIN = 0x3
EMBER_HIGH_SECURITY_SECURED_REJOIN      = 0x4
EMBER_HIGH_SECURITY_UNSECURED_JOIN      = 0x5
EMBER_HIGH_SECURITY_UNSECURED_REJOIN    = 0x7
ember_device_update = {\
    'EMBER_STANDARD_SECURITY_SECURED_REJOIN'  : 0x0,\
    'EMBER_STANDARD_SECURITY_UNSECURED_JOIN'  : 0x1,\
    'EMBER_DEVICE_LEFT'                       : 0x2,\
    'EMBER_STANDARD_SECURITY_UNSECURED_REJOIN' : 0x3,\
    'EMBER_HIGH_SECURITY_SECURED_REJOIN'      : 0x4,\
    'EMBER_HIGH_SECURITY_UNSECURED_JOIN'      : 0x5,\
    'EMBER_HIGH_SECURITY_UNSECURED_REJOIN'    : 0x7,\
}
ember_device_update_rev = {}
for tid,num in ember_device_update.items():
    ember_device_update_rev[num] = tid


# EmberKeyStatus
EMBER_APP_LINK_KEY_ESTABLISHED          = 0x01
EMBER_APP_MASTER_KEY_ESTABLISHED        = 0x02
EMBER_TRUST_CENTER_LINK_KEY_ESTABLISHED = 0x03
EMBER_KEY_ESTABLISHMENT_TIMEOUT         = 0x04
EMBER_KEY_TABLE_FULL                    = 0x05
EMBER_TC_RESPONDED_TO_KEY_REQUEST       = 0x06
EMBER_TC_APP_KEY_SENT_TO_REQUESTER      = 0x07
EMBER_TC_RESPONSE_TO_KEY_REQUEST_FAILED = 0x08
EMBER_TC_REQUEST_KEY_TYPE_NOT_SUPPORTED = 0x09
EMBER_TC_NO_LINK_KEY_FOR_REQUESTER      = 0x0A
EMBER_TC_REQUESTER_EUI64_UNKNOWN        = 0x0B
EMBER_TC_RECEIVED_FIRST_APP_KEY_REQUEST = 0x0C
EMBER_TC_TIMEOUT_WAITING_FOR_SECOND_APP_KEY_REQUEST = 0x0D
EMBER_TC_NON_MATCHING_APP_KEY_REQUEST_RECEIVED = 0x0E
EMBER_TC_FAILED_TO_SEND_APP_KEYS        = 0x0F
EMBER_TC_FAILED_TO_STORE_APP_KEY_REQUEST = 0x10
EMBER_TC_REJECTED_APP_KEY_REQUEST       = 0x11
ember_key_status = {\
    'EMBER_APP_LINK_KEY_ESTABLISHED'          : 0x01,\
    'EMBER_APP_MASTER_KEY_ESTABLISHED'        : 0x02,\
    'EMBER_TRUST_CENTER_LINK_KEY_ESTABLISHED' : 0x03,\
    'EMBER_KEY_ESTABLISHMENT_TIMEOUT'         : 0x04,\
    'EMBER_KEY_TABLE_FULL'                    : 0x05,\
    'EMBER_TC_RESPONDED_TO_KEY_REQUEST'       : 0x06,\
    'EMBER_TC_APP_KEY_SENT_TO_REQUESTER'      : 0x07,\
    'EMBER_TC_RESPONSE_TO_KEY_REQUEST_FAILED' : 0x08,\
    'EMBER_TC_REQUEST_KEY_TYPE_NOT_SUPPORTED' : 0x09,\
    'EMBER_TC_NO_LINK_KEY_FOR_REQUESTER'      : 0x0A,\
    'EMBER_TC_REQUESTER_EUI64_UNKNOWN'        : 0x0B,\
    'EMBER_TC_RECEIVED_FIRST_APP_KEY_REQUEST' : 0x0C,\
    'EMBER_TC_TIMEOUT_WAITING_FOR_SECOND_APP_KEY_REQUEST' : 0x0D,\
    'EMBER_TC_NON_MATCHING_APP_KEY_REQUEST_RECEIVED' : 0x0E,\
    'EMBER_TC_FAILED_TO_SEND_APP_KEYS'        : 0x0F,\
    'EMBER_TC_FAILED_TO_STORE_APP_KEY_REQUEST' : 0x10,\
    'EMBER_TC_REJECTED_APP_KEY_REQUEST'       : 0x11,\
}
ember_key_status_rev = {}
for tid,num in ember_key_status.items():
    ember_key_status_rev[num] = tid

#############################

