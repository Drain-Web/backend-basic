Set-StrictMode -Version latest
$ErrorActionPreference = "Stop"

echo "Ensure you are calling this script with the proper Python environment activated."
echo ""

echo "Cleaning database..."
python .\manage.py flush
echo ""

echo "Inserting module instances..."
python .\manage.py loaddata .\crud\fixtures\crud_fixture_moduleInstances.json
echo ""

echo "Inserting threshold warning levels..."
python .\manage.py loaddata .\crud\fixtures\crud_fixture_thresholdWarningLevel.json
echo ""

echo "Inserting threshold groups..."
python .\manage.py loaddata .\crud\fixtures\crud_fixture_thresholdGroup.json
echo ""

echo "Inserting level thresholds..."
python .\manage.py loaddata .\crud\fixtures\crud_fixture_levelThreshold.json
echo ""

echo "Inserting level threshold values..."
python .\manage.py loaddata .\crud\fixtures\crud_fixture_levelThresholdValues.json
echo ""

echo "Inserting threshold value sets..."
python .\manage.py loaddata .\crud\fixtures\crud_fixture_thresholdValueSets.json
echo ""

echo "Inserting boundaries..."
python .\manage.py loaddata .\crud\fixtures\crud_fixtureAuto_boundaries.json
echo ""

echo "Inserting map extents..."
python .\manage.py loaddata .\crud\fixtures\crud_fixtureAuto_maps.json
echo ""

echo "Inserting region..."
python .\manage.py loaddata .\crud\fixtures\crud_fixture_region.json
echo ""

echo "Inserting parameter groups..."
python .\manage.py loaddata .\crud\fixtures\crud_fixture_parametergroups.json
echo ""

echo "Inserting parameters..."
python .\manage.py loaddata .\crud\fixtures\crud_fixture_parameters.json
echo ""

echo "Inserting locations..."
python .\manage.py loaddata .\crud\fixtures\crud_fixture_locations.json
echo ""

echo "Inserting geo-event filters..."
python .\manage.py loaddata .\crud\fixtures\crud_fixtureAuto_geoevents.json
echo ""

Get-ChildItem ".\crud\fixtures\crud_fixture_timeseries\q" -Filter *.json | 
Foreach-Object {
  echo "Inserting timeseries $($_.Name)..."
  python .\manage.py loaddata $_.FullName
}
echo ""

Get-ChildItem ".\crud\fixtures\crud_fixture_timeseries\z" -Filter *.json | 
Foreach-Object {
  echo "Inserting timeseries $($_.Name)..."
  python .\manage.py loaddata $_.FullName
}
echo ""

Get-ChildItem ".\crud\fixtures\crud_fixture_timeseries\m-hist01" -Filter *.json | 
Foreach-Object {
  echo "Inserting timeseries $($_.Name)..."
  python .\manage.py loaddata $_.FullName
}
echo ""

echo "Finished loading fixtures."
