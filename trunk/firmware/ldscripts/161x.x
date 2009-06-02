/* Default linker script, for normal executables */
OUTPUT_FORMAT("elf32-msp430","elf32-msp430","elf32-msp430")
OUTPUT_ARCH(msp:16)
MEMORY
{
  text   (rx)       : ORIGIN = 0x4000,     LENGTH = 0xbfe0
  data   (rwx)      : ORIGIN = 0x1100,     LENGTH = 0x1400
  vectors (rw)      : ORIGIN = 0xffe0,     LENGTH = 32
  bootloader(rx)    : ORIGIN = 0x0c00,     LENGTH = 1K
  infomem(rx)       : ORIGIN = 0x1000,     LENGTH = 256
  infomemnobits(rx) : ORIGIN = 0x1000,     LENGTH = 256
}
SECTIONS
{
  /* Read-only sections, merged into text segment.  */
  .hash          : { *(.hash)             }
  .dynsym        : { *(.dynsym)           }
  .dynstr        : { *(.dynstr)           }
  .gnu.version   : { *(.gnu.version)      }
  .gnu.version_d   : { *(.gnu.version_d)  }
  .gnu.version_r   : { *(.gnu.version_r)  }
  .rel.init      : { *(.rel.init) }
  .rela.init     : { *(.rela.init) }
  .rel.text      :
    {
      *(.rel.text)
      *(.rel.text.*)
      *(.rel.gnu.linkonce.t*)
    }
  .rela.text     :
    {
      *(.rela.text)
      *(.rela.text.*)
      *(.rela.gnu.linkonce.t*)
    }
  .rel.fini      : { *(.rel.fini) }
  .rela.fini     : { *(.rela.fini) }
  .rel.rodata    :
    {
      *(.rel.rodata)
      *(.rel.rodata.*)
      *(.rel.gnu.linkonce.r*)
    }
  .rela.rodata   :
    {
      *(.rela.rodata)
      *(.rela.rodata.*)
      *(.rela.gnu.linkonce.r*)
    }
  .rel.data      :
    {
      *(.rel.data)
      *(.rel.data.*)
      *(.rel.gnu.linkonce.d*)
    }
  .rela.data     :
    {
      *(.rela.data)
      *(.rela.data.*)
      *(.rela.gnu.linkonce.d*)
    }
  .rel.ctors     : { *(.rel.ctors)        }
  .rela.ctors    : { *(.rela.ctors)       }
  .rel.dtors     : { *(.rel.dtors)        }
  .rela.dtors    : { *(.rela.dtors)       }
  .rel.got       : { *(.rel.got)          }
  .rela.got      : { *(.rela.got)         }
  .rel.bss       : { *(.rel.bss)          }
  .rela.bss      : { *(.rela.bss)         }
  .rel.plt       : { *(.rel.plt)          }
  .rela.plt      : { *(.rela.plt)         }
  /* Internal text space.  */
  .text :
  {
    . = ALIGN(2);
    *(.init)
    KEEP(*(.init))
    *(.init0)  /* Start here after reset.               */
    KEEP(*(.init0))
    *(.init1)  /* User definable.                       */
    KEEP(*(.init1))
    *(.init2)  /* Initialize stack.                     */
    KEEP(*(.init2))
    *(.init3)  /* Initialize hardware, user definable.  */
    KEEP(*(.init3))
    *(.init4)  /* Copy data to .data, clear bss.        */
    KEEP(*(.init4))
    *(.init5)  /* User definable.                       */
    KEEP(*(.init5))
    *(.init6)  /* C++ constructors.                     */
    KEEP(*(.init6))
    *(.init7)  /* User definable.                       */
    KEEP(*(.init7))
    *(.init8)  /* User definable.                       */
    KEEP(*(.init8))
    *(.init9)  /* Call main().                          */
    KEEP(*(.init9))
     __ctors_start = . ;
     *(.ctors)
     KEEP(*(.ctors))
     __ctors_end = . ;
     __dtors_start = . ;
     *(.dtors)
     KEEP(*(.dtors))
     __dtors_end = . ;
    . = ALIGN(2);
    *(.text)
    . = ALIGN(2);
    *(.text.*)
    . = ALIGN(2);
    *(.fini9)  /* Jumps here after main(). User definable.  */
    KEEP(*(.fini9))
    *(.fini8)  /* User definable.                           */
    KEEP(*(.fini8))
    *(.fini7)  /* User definable.                           */
    KEEP(*(.fini7))
    *(.fini6)  /* C++ destructors.                          */
    KEEP(*(.fini6))
    *(.fini5)  /* User definable.                           */
    KEEP(*(.fini5))
    *(.fini4)  /* User definable.                           */
    KEEP(*(.fini4))
    *(.fini3)  /* User definable.                           */
    KEEP(*(.fini3))
    *(.fini2)  /* User definable.                           */
    KEEP(*(.fini2))
    *(.fini1)  /* User definable.                           */
    KEEP(*(.fini1))
    *(.fini0)  /* Infinite loop after program termination.  */
    KEEP(*(.fini0))
    *(.fini)
    KEEP(*(.fini))
    _etext = .;
  }  > text
  .data   :
  {
     PROVIDE (__data_start = .) ;
    . = ALIGN(2);
    *(.data)
    *(SORT_BY_ALIGNMENT(.data.*))
    . = ALIGN(2);
    *(.gnu.linkonce.d*)
    . = ALIGN(2);
     _edata = . ;
  }  > data AT > text
    PROVIDE (__data_load_start = LOADADDR(.data) );
    PROVIDE (__data_size = SIZEOF(.data) );
  /* Bootloader.  */
  .bootloader   :
  {
     PROVIDE (__boot_start = .) ;
    *(.bootloader)
    . = ALIGN(2);
    *(.bootloader.*)
  }  > bootloader
  /* Information memory.  */
  .infomem   :
  {
    *(.infomem)
    . = ALIGN(2);
    *(.infomem.*)
  }  > infomem
  /* Information memory (not loaded into MPU).  */
  .infomemnobits   :
  {
    *(.infomemnobits)
    . = ALIGN(2);
    *(.infomemnobits.*)
  }  > infomemnobits
  .bss   :
  {
     PROVIDE (__bss_start = .) ;
    *(.bss)
    *(SORT_BY_ALIGNMENT(.bss.*))
    *(COMMON)
     PROVIDE (__bss_end = .) ;
     _end = . ;
  }  > data
    PROVIDE (__bss_size = SIZEOF(.bss) );
  .noinit   :
  {
     PROVIDE (__noinit_start = .) ;
    *(.noinit)
    *(.noinit.*)
    *(COMMON)
     PROVIDE (__noinit_end = .) ;
     _end = . ;
  }  > data
  .vectors  :
  {
     PROVIDE (__vectors_start = .) ;
    *(.vectors*)
    KEEP(*(.vectors*))
     _vectors_end = . ;
  }  > vectors
  /* Stabs for profiling information*/
  .profiler 0 : { *(.profiler) }
  /* Stabs debugging sections.  */
  .stab 0 : { *(.stab) }
  .stabstr 0 : { *(.stabstr) }
  .stab.excl 0 : { *(.stab.excl) }
  .stab.exclstr 0 : { *(.stab.exclstr) }
  .stab.index 0 : { *(.stab.index) }
  .stab.indexstr 0 : { *(.stab.indexstr) }
  .comment 0 : { *(.comment) }
  /* DWARF debug sections.
     Symbols in the DWARF debugging sections are relative to the beginning
     of the section so we begin them at 0.  */
  /* DWARF 1 */
  .debug          0 : { *(.debug) }
  .line           0 : { *(.line) }
  /* GNU DWARF 1 extensions */
  .debug_srcinfo  0 : { *(.debug_srcinfo) }
  .debug_sfnames  0 : { *(.debug_sfnames) }
  /* DWARF 1.1 and DWARF 2 */
  .debug_aranges  0 : { *(.debug_aranges) }
  .debug_pubnames 0 : { *(.debug_pubnames) }
  /* DWARF 2 */
  .debug_info     0 : { *(.debug_info) *(.gnu.linkonce.wi.*) }
  .debug_abbrev   0 : { *(.debug_abbrev) }
  .debug_line     0 : { *(.debug_line) }
  .debug_frame    0 : { *(.debug_frame) }
  .debug_str      0 : { *(.debug_str) }
  .debug_loc      0 : { *(.debug_loc) }
  .debug_macinfo  0 : { *(.debug_macinfo) }
  /* DWARF 3 */
  .debug_pubtypes 0 : { *(.debug_pubtypes) }
  .debug_ranges   0 : { *(.debug_ranges) }
  PROVIDE (__stack = 0x2500) ;
  PROVIDE (__data_start_rom = _etext) ;
  PROVIDE (__data_end_rom   = _etext + SIZEOF (.data)) ;
  PROVIDE (__noinit_start_rom = _etext + SIZEOF (.data)) ;
  PROVIDE (__noinit_end_rom = _etext + SIZEOF (.data) + SIZEOF (.noinit)) ;
  PROVIDE (__subdevice_has_heap = 0) ;
}
