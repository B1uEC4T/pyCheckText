$python_path = py -c "import sys; import os;  print(sys.executable)"
$python_dir = [System.IO.FileInfo]$python_path
$python_dir = $python_dir.Directory.FullName

$msgfmt = Join-Path -Path $python_dir -ChildPath "Tools/i18n/msgfmt.py"

$test_files = Get-ChildItem -Path ..\ -Filter *.po -Recurse

foreach ($file in $test_files) {
    $file_name_trimmed =  $file.Directory.FullName + "\" + [System.IO.Path]::GetFileNameWithoutExtension($file)
    $input_str = $file_name_trimmed + ".po"
    $output_str = "$file_name_trimmed.mo"
    $params = $msgfmt, '-o', $output_str, $input_str
    & $python_path @params
}