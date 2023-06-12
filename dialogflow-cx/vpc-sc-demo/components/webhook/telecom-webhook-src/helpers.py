# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Helper module for Telecommunications webhook function."""


from datetime import date


def get_date_details(bill_state):
    """Get date details helper function."""

    month_names = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    today = date.today()
    # index starts with 0
    first_month_name = month_names[today.month - 1]
    first_day = today.replace(day=1)
    first_day_str = str(first_day)

    last_month_name = month_names[today.month - 2]
    last_month_first_day_str = str(today.replace(day=1, month=today.month - 1))
    second_last_month_name = month_names[today.month - 3]
    if bill_state == "current":
        return [first_month_name, first_day_str, last_month_name]
    return [last_month_name, last_month_first_day_str, second_last_month_name]
