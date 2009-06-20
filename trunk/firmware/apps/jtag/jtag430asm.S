.globl jtag430_tclk_flashpulses
.type jtag430_tclk_flashpulses,@function    /* declare main as a function */
	
jtag430_tclk_flashpulses:
	sub #1, r15
	bis.b #2, &0x0031	;SETTCLK
	nop
	nop
	nop
	bic.b #2, &0x0031	;CLRTCLK
	tst r15
	jnz jtag430_tclk_flashpulses
	ret

