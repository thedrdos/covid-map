SECONDS=0
dur_arr=(0)
echo "##########################################"
echo "Running: get_data_for_maps.py"
echo "##########################################"
python get_data_for_maps.py || exit 1
dur_arr+=$SECONDS
echo "Completed in: $(($($dur_arr[-1]-$dur_arr[-2]) / 60)) minutes and $(($($dur_arr[-1]-$dur_arr[-2]) % 60)) seconds."

echo "##########################################"
echo "Running: process_data_for_maps.py"
echo "##########################################"
python process_data_for_maps.py || exit 2
dur_arr+=$SECONDS
echo "Completed in: $(($((${dur_arr[${#dur_arr[@]}-1]}-${dur_arr[${#dur_arr[@]}-2]})) / 60)) minutes and $(($((${dur_arr[${#dur_arr[@]}-1]}-${dur_arr[${#dur_arr[@]}-2]})) % 60)) seconds."

echo "##########################################"
echo "Running: make_external_datafiles.py"
echo "##########################################"
python make_external_datafiles.py || exit 2
dur_arr+=$SECONDS
echo "Completed in: $(($((${dur_arr[${#dur_arr[@]}-1]}-${dur_arr[${#dur_arr[@]}-2]})) / 60)) minutes and $(($((${dur_arr[${#dur_arr[@]}-1]}-${dur_arr[${#dur_arr[@]}-2]})) % 60)) seconds."

echo "##########################################"
echo "Running: map_4mon_standalone.py"
echo "##########################################"
python map_4mon_standalone.py || exit 3
dur_arr+=$SECONDS
echo "Completed in: $(($((${dur_arr[${#dur_arr[@]}-1]}-${dur_arr[${#dur_arr[@]}-2]})) / 60)) minutes and $(($((${dur_arr[${#dur_arr[@]}-1]}-${dur_arr[${#dur_arr[@]}-2]})) % 60)) seconds."

echo "##########################################"
echo "Running: map_4mon_external_data.py"
echo "##########################################"
python map_4mon_external_data.py || exit 3
dur_arr+=$SECONDS
echo "Completed in: $(($((${dur_arr[${#dur_arr[@]}-1]}-${dur_arr[${#dur_arr[@]}-2]})) / 60)) minutes and $(($((${dur_arr[${#dur_arr[@]}-1]}-${dur_arr[${#dur_arr[@]}-2]})) % 60)) seconds."

echo "##########################################"
echo "Running: make_website.py"
echo "##########################################"
python make_website.py || exit 4
dur_arr+=$SECONDS
echo "Completed in: $(($((${dur_arr[${#dur_arr[@]}-1]}-${dur_arr[${#dur_arr[@]}-2]})) / 60)) minutes and $(($((${dur_arr[${#dur_arr[@]}-1]}-${dur_arr[${#dur_arr[@]}-2]})) % 60)) seconds."

echo "##########################################"
echo "Script completed in: "
duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds."
