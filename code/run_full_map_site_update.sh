SECONDS=0
echo "##########################################"
echo "Running: get_data_for_maps.py"
echo "##########################################"
python get_data_for_maps.py

echo "##########################################"
echo "Running: process_data_for_maps.py"
echo "##########################################"
python process_data_for_maps.py

echo "##########################################"
echo "Running: map_demo_sandbox.py"
echo "##########################################"
python map_4mon_standalone.py

echo "##########################################"
echo "Running: make_website.py"
echo "##########################################"
python make_website.py



echo "##########################################"
echo "Script completed in: "
duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds."
