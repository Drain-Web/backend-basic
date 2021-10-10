#!/bin/bash


echo "Ensure you are calling this script with the proper Python environment activated."
echo ""

declare -a TS_FIXTURES=("q_d050t065USGSobs" "q_d115t140USGSobs" "q_sim_d080t090Hist01")
for ts_fdna in "${TS_FIXTURES[@]}"; do
  TS_FDPA="./crud/fixtures/crud_fixture_timeseries/${ts_fdna}"
  TS_GLOB="${TS_FDPA}/*.json"
  for json_fipa in ${TS_GLOB}; do
    json_file_name=$(basename -- "$json_fipa")
    echo "Inserting timeseries ${json_file_name}..."
    python ./manage.py loaddata ${json_fipa}
  done
  echo ""
done

echo "Finished loading fixtures."
