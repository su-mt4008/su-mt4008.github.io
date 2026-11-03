# Functions the report uses. Keep the report readable by moving longer code here.

summarise_by <- function(df, group, value) {
  df |>
    dplyr::group_by(dplyr::across(dplyr::all_of(group))) |>
    dplyr::summarise(
      n = dplyr::n(),
      mean = round(mean(.data[[value]]), 1),
      sd = round(sd(.data[[value]]), 1),
      .groups = "drop"
    )
}
