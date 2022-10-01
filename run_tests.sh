#!/bin/bash

# A utility script to run the tests. To be used as a template/reminder.

TEST_FOLDER_PATH="tests/exp"

PYTEST="pytest -rA -v --pdb --showlocals"

${PYTEST} "${TEST_FOLDER_PATH}/test_time_to_deanonimize.py::test_plot_avg_time_to_deanonymize_vs_num_servers"
