#!/bin/bash

send_error()
{
echo "`date +%Y.%m.%d-%T`: send_error(): ошибка при выполнении команды: ${1}" >> ${log}
echo "`date +%Y.%m.%d-%T`: send_error(): отправляю письмо пользователю: ${email_error_to}" >> ${log}
subject=`echo "OSM-сервер: ОШИБКА! Сбой обновления данных о загрузке подстанций"|base64 -w 0`
sendEmail -o tls=no -f osm_import@rsprim.ru -o message-charset=utf-8 -t "${email_error_to}" -s ${email_server} -u "=?utf-8?b?${subject}?=" \
-m "Письмо сгенерировано автоматически.
Произошёл сбой на сервере `hostname` в подсистеме OSM. При попытке обновления данных о загрузке подстанций
произошла ошибка. Задачей обновления было регулярное обновление данных, преобразование их в нужный формат и
отображение данных о загрузке подстанций на карте. В данный момент данные о загрузке подстанций на карте либо не отображаются, либо устарели.

======== Техническая информация: ========
Сбой произошёл при выполнении команды: 
${1}

В обычной ситуации данная команда не должна завершаться с ошибкой. Значит на то были веские причины.

Последние строки лога этого ($0) скрипта:
`tail -n 20 ${log}`
" &>> ${log}
}

if [ -z ${1} ]
then
	echo "Нужен один аргумент - конфиг-файл"
	exit 1
fi

source "${1}"

echo "`date +%Y.%m.%d-%T`: ============ start $0 ==============" >> ${log}

rm "${import_data_file}"
wget -q ${load_xml_url} -O "${import_data_file}"

if [ ! 0 -eq $? ]
then
	send_error "wget ${load_xml_url} -O ${import_data_file}"
	exit 1
fi
size="`stat -c %s ${import_data_file}`"
echo "`date +%Y.%m.%d-%T`: успешно скачали данные о загрузке подстанций. Файл создан: `stat -c %z ${import_data_file}`, размер: $size байт" >> ${log}
if [ 0 -eq $size ]
then
	echo "`date +%Y.%m.%d-%T`: скачанный файл нулевого размера - ОШИБКА!" >> ${log}
	send_error "wget -q ${load_xml_url} -O ${import_data_file}"
	exit 1
fi

# Конвертация:
${parser} ${import_data_file} ${out_file}
if [ ! 0 -eq $? ]
then
	send_error "${parser} ${import_data_file} ${out_file}"
	exit 1
fi

# Запуск импорта данных в карту:
${osmbot_script} ${osmbot_config} 
if [ ! 0 -eq $? ]
then
	send_error "${osmbot_script} ${osmbot_config}"
	exit 1
fi


echo "`date +%Y.%m.%d-%T`: ============ success end $0 ==============" >> ${log}
exit 0
