// Get the current month, first day of current month and last month values
// based on today's date
module.exports = {
  get_date_details: function (bill_state) {
    const monthNames = [
      'January',
      'February',
      'March',
      'April',
      'May',
      'June',
      'July',
      'August',
      'September',
      'October',
      'November',
      'December',
    ];
    let today = new Date();
    let first_month_name = monthNames[today.getMonth()];
    let firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    let first_day_str =
      first_month_name +
      ' 0' +
      firstDay.getDate() +
      ', ' +
      firstDay.getFullYear();

    let last_month_name = monthNames[today.getMonth() - 1];
    let last_month_first_day_str =
      last_month_name +
      ' 0' +
      firstDay.getDate() +
      ', ' +
      firstDay.getFullYear();
    let second_last_month_name = monthNames[today.getMonth() - 2];

    // If bill state is current month vs previous month
    if (bill_state.toString() == 'current') {
      return [first_month_name, first_day_str, last_month_name];
    } else {
      return [
        last_month_name,
        last_month_first_day_str,
        second_last_month_name,
      ];
    }
  },
};
