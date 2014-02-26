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

// this function initializes the stack for a given task so that
// we can start the task calling the return_to_task macro
inline initialize_task(sp, entry) {
    tsx                 // get current stack pointer
    txa                 // x -> a
    tay                 // a -> y

    ldx     sp          // put task stack pointer in x
    txs                 // set stack pointer to task stack pointer
    lda     hi(entry)   // get high byte of task entry address
    pha                 // push high byte of task entry address on task stack
    lda     lo(entry)   // get low byte of task entry address
    pha                 // push low byte of task entry address on task stack
    lda     #$34        // put standard cpu status flags in a
    pha                 // push standard cpu status flags on task stack
    lda     #$0         // a = 0
    pha                 // push initial a value on stack
    pha                 // push initial x value on stack
    pha                 // push initial y value on stack

    tya                 // y -> a
    tax                 // a -> x
    txs                 // restore the stack pointer
}

// this macro handles storing the current task registers on its stack
inline save_task_context() {
    pha
    txa
    pha
    tya
    pha
}

// this macro handles restoring a task registers from its stack
inline load_task_context() {
    pla                 // pop the y value
    tay                 // initialize y
    pla                 // pop the x value
    tax                 // initialize x
    pla                 // pop the a value
}

// this handles storing the current stack pointer in memory, updating the
// current task index in memory and then loading the new task's stack pointer
inline switch_tasks(cur_task) {
    ldy     cur_task    // load current task index into y
    tsx                 // put the current stack pointer in x
    stx     $00,y       // store current stack pointer into current task sp var

    // this updates the current task index
    lda     #1          // a = 1
    eor     cur_task    // a = cur_task ^ a  (this flips from 0 to 1/1 to 0)
    sta     cur_task    // cur_task = a
   
    tay                 // make y equal the new task index
    ldx     $00,y       // load new task stack pointer from its task sp var
    txs                 // set stack pointer to task stack pointer
}

// this function will start the threading system by restoring
// the given task context, setting the cpu status, and calling
// rts to jump to it.  this can be called from a regular function
// to start the threading system.
inline start_all_tasks(first_task) {
    ldy     first_task  // get the index of the first task
    ldx     $00,y       // load its stack pointer into x
    txs                 // set stack pointer to first task sp
    load_task_context() // load task context from its stack
    plp                 // load task cpu status, this will clear interrupt disable flag
    rts                 // return to the task entry point
}

// this is the interrupt handler to hook up to the timer IRQ to
// implement task switching
interrupt context_switch() {
    // save the current task context on its stack
    save_task_context()

    // switch tasks
    switch_tasks(current_task)

    // load the task context from tnew task stack
    load_task_context()

    cli                 // clear the interrupt flag
    rti                 // return back to the new task
}

