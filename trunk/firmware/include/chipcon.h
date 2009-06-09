//These high-level functions are implemented in chipcon.c.


//! Erase a chipcon chip.
void cc_chip_erase();
//! Write the configuration byte.
void cc_wr_config(unsigned char config);
//! Read the configuration byte.
unsigned char cc_rd_config();
//! Read the status register.
unsigned char cc_read_status();
//! Read the CHIP ID bytes.
unsigned short cc_get_chip_id();
//! Get the PC
unsigned short cc_get_pc();
//! Set a hardware breakpoint.
void cc_set_hw_brkpnt(unsigned short);

//! Halt the CPU.
void cc_halt();
//! Resume the CPU.
void cc_resume();
//! Step an instruction
void cc_step_instr();

