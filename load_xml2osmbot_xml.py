#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from lxml import etree
import sys

DEBUG=False
#DEBUG=True

if len(sys.argv) < 3:
	print("Необходимо два аргумента - входной файл и выходной файл")
	sys.exit(1)

def add_patchset(osmpatch, name, tags):
	patchset= etree.SubElement(osmpatch, "patchset")

	# Что ищем:
	find = etree.SubElement(patchset, "find")
	type_node=etree.Element("type", nodes="yes", ways="yes", relation="yes")
	find.append(type_node)

	# key1=value1
	tag = etree.SubElement(find, "tag")
#key=etree.Element("key", full_match="yes")
	key=etree.Element("key")
	key.text="power"
	tag.append(key)
#value=etree.Element("value", full_match="yes", case_sensitive='yes')
	value=etree.Element("value")
	value.text="sub_station"
	tag.append(value)

	# key2=value2
	tag = etree.SubElement(find, "tag")
#key=etree.Element("key", full_match="yes")
	key=etree.Element("key")
	key.text="ref"
	tag.append(key)
#value=etree.Element("value", full_match="yes", case_sensitive='yes')
	value=etree.Element("value")
	value.text=name
	tag.append(value)

	# На что меняем:
	add = etree.SubElement(patchset, "add")
	for k in tags:
		key=etree.Element("tag", k=k, v=tags[k])
		add.append(key)

# ================= main =================
# Формируем структуру патчсета:
osmpatch = etree.Element("osmpatch")

xml = etree.parse(sys.argv[1])
root = xml.getroot()
#print (etree.tostring(root,pretty_print=True, encoding='unicode'))
for node in root:
	if DEBUG:
		print node.tag
	if node.tag=="records":
		for record in node:
			name=""
			tags={}
			for item in record:
				if DEBUG:
					print item.tag, item.text
				if item.tag==u"ТП":
					name=item.text
				elif item.tag==u"ДатаСреза":
					tags["power_usage_date"]=u"КДЗ %s" % item.text
					tags["power_usage_comment"]=u"С учётом перспективной нагрузки на %s" % item.text
				elif item.tag==u"РезЗамеровМВт":
					tags["power_usage_mvt_real_kdz"]=item.text.replace(",",".")
				elif item.tag==u"ДопустимаяНагрузкаМВт":
					tags["power_usage_mvt_dopustima"]=item.text.replace(",",".")
				elif item.tag==u"ЗагрузкаТППроц":
					tags["power_usage_percent"]=item.text.replace(",",".")
				elif item.tag==u"НагрВсего":
					tags["power_usage_mvt_perspectiv_all"]=item.text.replace(",",".")
			if name=="":
				print("error! name=''")
				sys.exit(1)
			add_patchset(osmpatch,name,tags)
			
if DEBUG:
	print (etree.tostring(osmpatch,pretty_print=True, encoding='unicode'))

string=etree.tostring(osmpatch, xml_declaration=True, encoding='UTF-8', pretty_print=True )
f=open(sys.argv[2],"w+")
f.write(string)
f.close



