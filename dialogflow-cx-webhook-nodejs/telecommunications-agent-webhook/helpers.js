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
    const today = new Date();
    const first_month_name = monthNames[today.getMonth()];
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    const first_day_str =
      first_month_name +
      ' 0' +
      firstDay.getDate() +
      ', ' +
      firstDay.getFullYear();

    const last_month_name = monthNames[today.getMonth() - 1];
    const last_month_first_day_str =
      last_month_name +
      ' 0' +
      firstDay.getDate() +
      ', ' +
      firstDay.getFullYear();
    const second_last_month_name = monthNames[today.getMonth() - 2];

    // If bill state is current month vs previous month
    if (bill_state.toString() === 'current') {
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
