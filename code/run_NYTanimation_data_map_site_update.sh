# List of scripts to run
script_list=(
"MakeDateBasedExtDataFiles.py"
"AnimateNYT_custom.py"
"make_website.py")

arg_list=(
""
""
""
""
""
""
""
""
"mobile"
"")

# The following is the actual script execution
SECONDS=0
dur_arr=(0)
i=0
for s in ${script_list[@]};
do
  echo "####################################"
  echo "Running: " $s ${arg_list[$i]}
  echo "####################################"
  python $s ${arg_list[$i]} || exit $i

  ((i=i+1))
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
