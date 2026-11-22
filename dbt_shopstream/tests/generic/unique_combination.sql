{#
  Fails if the combination of `columns` is not unique.
  (Same idea as dbt_utils.unique_combination_of_columns, without the package.)
#}
{% test unique_combination(model, columns) %}
SELECT {{ columns | join(', ') }}, count(*) AS n
FROM {{ model }}
GROUP BY {{ columns | join(', ') }}
HAVING count(*) > 1
{% endtest %}
