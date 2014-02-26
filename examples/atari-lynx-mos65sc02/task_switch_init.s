/* 
 * HLAKit
 * Copyright (c) 2010 David Huseby. All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without modification, are
 * permitted provided that the following conditions are met:
 * 
 *    1. Redistributions of source code must retain the above copyright notice, this list of
 *       conditions and the following disclaimer.
 * 
 *    2. Redistributions in binary form must reproduce the above copyright notice, this list
 *       of conditions and the following disclaimer in the documentation and/or other materials
 *       provided with the distribution.
 * 
 * THIS SOFTWARE IS PROVIDED BY DAVID HUSEBY ``AS IS'' AND ANY EXPRESS OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
 * FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL DAVID HUSEBY OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
 * ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
 * ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * 
 * The views and conclusions contained in the software and documentation are those of the
 * authors and should not be interpreted as representing official policies, either expressed
 * or implied, of David Huseby.
 */

/*
 * ClassicGameDev.com Example Task Switching
 */

#include <task_switch.h>

#define IRQ_ADDR_HI  $FFFF
#define IRQ_ADDR_LO  $FFFE

byte task0_sp        : $0 = #$ff  // task 0 stack pointer storage
byte task1_sp        : $1 = #$7f  // task 1 stack pointer storage
byte current_task    : $2 = #0    // current task index

#ram.org 0x0200

// make this the function that the second stage loader
// loads and runs.  it handles further initializing the system,
// initializing the tasks and starting the task switching
function noreturn startup() {
    // disable interrupts
    sei

    // set the irq handler pointer to our context_switch function
    lda    hi(context_switch)
    sta    IRQ_ADDR_HI
    lda    lo(context_switch)
    sta    IRQ_ADDR_LO

    // initialize one of the handy interrupts to fire at 30 Hz
    initialize_timer()

    // initialize the stacks for the two tasks
    initialize_task(task0_sp, game_loop)
    initialize_task(task1_sp, asset_loader)

    // start the task system, this will set the CPU status flags to
    // a known value for the first task which will clear the disable
    // interrupts bit
    start_all_tasks(current_task)
}

function noreturn game_loop() {
    forever {
        // this is the main game loop
    }
}

function noreturn asset_loader() {
    forever {
        // this is the asset loader
    }
}

#ram.end
