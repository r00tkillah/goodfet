/*! \file openocd.c
  \author Dave Huseby <dave at linuxprogrammer.org>
  \brief OpenOCD firmware
*/


#include "platform.h"
#include "command.h"

#define OPENOCD_APP

//! Handles a monitor command.
void openocd_handle_fn(uint8_t const app,
					   uint8_t const verb,
					   uint32_t const len);

// define the openocd app's app_t
app_t const openocd_app = {

	/* app number */
	OPENOCD,

	/* handle fn */
	openocd_handle_fn,

	/* name */
	"OpenOCD",

	/* desc */
	"\tThe OpenOCD app handles the OpenOCD protocol.\n"
};

//! handles OpenOCD commands
void openocd_handle_fn(uint8_t const app,
					   uint8_t const verb,
					   uint32_t const len)
{
	switch(verb)
	{
		case START:
			txdata(app,verb,0);
			break;

		case STOP:
			txdata(app,verb,0);
			break;

		case SETUP:
			txdata(app,verb,0);
			break;

		default:
			txdata(app,NOK,0);
	}
}


