#!/bin/bash

run_task() {
    local ROUND=$1
    local WEIGHT=$2
    local satTrd=$3
    local STARTR=$4
    local index=$5

    python -u /home/user/lhn/fast_verify_new_model/code/solve_verify_model.py \
        -r $ROUND  -w $WEIGHT -m $STARTR -satTrd $satTrd \
        -f /home/user/lhn/fast_verify_new_model/constest \
        -sat cryptominisat5 \
        > /home/user/lhn/fast_verify_new_model/code/Sol4R_check5R_w${WEIGHT}_cms_t${satTrd}_start${STARTR}_kmt_test.log 2>&1
    
    if [ $? -ne 0 ]; then
        echo "Task $index failed" >> ${log_dir}/error.log
    fi
    
}

# 启动任务
run_task 4 310 20 0 1 & 

wait