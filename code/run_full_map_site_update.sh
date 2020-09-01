# List of scripts to run
script_list=(
"match_data_and_maps.py"
"process_data_and_maps.py"
"make_external_datafiles.py"
"map_4mon_external_data.py"
"map_4mon_standalone.py"
"make_website.py")

# The following is the actual script execution
SECONDS=0
dur_arr=(0)
i=0
for s in ${script_list[@]};
do
  ((i=i+1))
  echo "####################################"
  echo "Running: " $s
  echo "####################################"
  python $s || exit $i

  dur_arr+=($SECONDS)
  echo "Completed in: $(($((${dur_arr[${#dur_arr[@]}-1]}-${dur_arr[${#dur_arr[@]}-2]})) / 60)) minutes and $(($((${dur_arr[${#dur_arr[@]}-1]}-${dur_arr[${#dur_arr[@]}-2]})) % 60)) seconds."
done

# Provide a summary of script runtimes
echo "======================="
echo "Summary:"
echo "======================="
i=0
for s in ${script_list[@]};
do
  ((i=i+1))
  echo $s
  echo "    $(($((${dur_arr[$i]}-${dur_arr[$i-1]})) / 60)) minutes and $(($((${dur_arr[$i]}-${dur_arr[$i-1]})) % 60)) seconds."
done
echo "======================="
echo "$(date)" # Show todays date
echo "Script completed in: "
duration=$SECONDS
echo "    $(($duration / 60)) minutes and $(($duration % 60)) seconds."
