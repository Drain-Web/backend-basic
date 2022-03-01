#!/bin/bash

echo "Ensure you are calling this script with the proper Python environment activated."
echo ""

echo "Reading files in..."
echo " '${1}'."

echo "Cleaning database..."
python ./manage.py flush
echo ""

echo "Inserting module instances..."
python ./manage.py loaddata ${1}/crud_fixture_moduleInstances.json
echo ""

echo "Inserting threshold warning levels..."
python ./manage.py loaddata ${1}/crud_fixture_thresholdWarningLevel.json
echo ""

echo "Inserting threshold groups..."
python ./manage.py loaddata ${1}/crud_fixture_thresholdGroup.json
echo ""

echo "Inserting level thresholds..."
python ./manage.py loaddata ${1}/crud_fixture_levelThreshold.json
echo ""

echo "Inserting level threshold values..."
python ./manage.py loaddata ${1}/crud_fixture_levelThresholdValues.json
echo ""

echo "Inserting threshold value sets..."
python ./manage.py loaddata ${1}/crud_fixture_thresholdValueSets.json
echo ""

echo "Inserting boundaries..."
python ./manage.py loaddata ${1}/auto/crud_fixtureAuto_boundaries.json
echo ""

echo "Inserting map extents..."
python ./manage.py loaddata ${1}/auto/crud_fixtureAuto_maps.json
echo ""

echo "Inserting region..."
python ./manage.py loaddata ${1}/crud_fixture_region.json
echo ""

echo "Inserting parameter groups..."
python ./manage.py loaddata ${1}/crud_fixture_parametergroups.json
echo ""

echo "Inserting parameters..."
python ./manage.py loaddata ${1}/crud_fixture_parameters.json
echo ""

echo "Inserting locations..."
python ./manage.py loaddata ${1}/crud_fixture_locations.json
echo ""

echo "Inserting geo-event filters..."
echo " FROM: "${1}"/auto/crud_fixtureAuto_geoevents.json"
python ./manage.py loaddata ${1}/auto/crud_fixtureAuto_geoevents.json
echo ""

for json_file in ${1}/timeseries/*.json; do
  json_file_name=$(basename -- "$json_file")
  echo "Inserting timeseries ${json_file_name}..."
  python ./manage.py loaddata ${json_file}
  python ./manage.py loaddata ${json_file}
done
echo ""

echo "Finished loading fixtures."
