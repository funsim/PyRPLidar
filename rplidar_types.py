'''
RPLidar Types Definition

translated from <rptypes.h> of RPLidar SDK v1.4.5
by Tong Wang

 * Copyright (c) 2014, RoboPeak
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without 
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, 
 *    this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice, 
 *    this list of conditions and the following disclaimer in the documentation 
 *    and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
 * OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, 
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *

 *
 *  RoboPeak LIDAR System
 *  Common Types definition
 *
 *  Copyright 2009 - 2014 RoboPeak Team
 *  http://www.robopeak.com
 *  
'''



class RPLidarError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "[RPLidar ERROR] %s\n" % str(self.message)

    def log(self):
        ret = "%s" % str(self.message)
        if(hasattr(self, "reason")):
            return "".join([ret, "\n==> %s" % str(self.reason)])
        return ret



#RESULT_OK = 0
#RESULT_FAIL_BIT = 0x80000000
#RESULT_ALREADY_DONE = 0x20
#RESULT_INVALID_DATA = (0x8000 | RESULT_FAIL_BIT)
#RESULT_OPERATION_FAIL = (0x8001 | RESULT_FAIL_BIT)
#RESULT_OPERATION_TIMEOUT = (0x8002 | RESULT_FAIL_BIT)
#RESULT_OPERATION_STOP = (0x8003 | RESULT_FAIL_BIT)
#RESULT_OPERATION_NOT_SUPPORT = (0x8004 | RESULT_FAIL_BIT)
#RESULT_FORMAT_NOT_SUPPORT = (0x8005 | RESULT_FAIL_BIT)
#RESULT_INSUFFICIENT_MEMORY = (0x8006 | RESULT_FAIL_BIT)

