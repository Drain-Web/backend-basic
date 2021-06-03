echo "Ensure you are calling this script with the proper Python environment activated."
echo ""

echo "Cleaning database..."
python .\manage.py flush
echo ""

<# #>
echo "Inserting region..."
python .\manage.py loaddata .\crud\fixtures\crud_fixture_region.json
echo ""

echo "Inserting locations..."
python .\manage.py loaddata .\crud\fixtures\crud_fixture_locations.json
echo ""

echo "Inserting geo-event filters..."
python .\manage.py loaddata .\crud\fixtures\crud_fixture_geoevts.json
echo ""

Get-ChildItem ".\crud\fixtures\crud_fixture_timeseries\" -Filter *.json | 
Foreach-Object {
  echo "Inserting timeseries $($_.Name)..."
  python .\manage.py loaddata $_.FullName
}
echo ""
echo "Finished loading fixtures."
