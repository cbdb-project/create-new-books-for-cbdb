import csv
from bs4 import BeautifulSoup
import requests
import re
from datetime import date
# pip install pypinyin
from pypinyin import lazy_pinyin

def get_new_textid(url_get_last_text_id):
    html_soup = BeautifulSoup(requests.get(url_get_last_text_id).text, features="lxml")
    c_textid = html_soup.find('input', {"name":"c_textid"})
    return int(c_textid['value'])

# create output, create db headline
output = [["\ufefftts_sysno", "c_textid", "c_title_chn", "c_title", "c_title_trans", "c_text_type_id", "c_text_year", "c_text_nh_code", "c_text_nh_year", "c_text_range_code", "c_bibl_cat_code", "c_extant", "c_text_country", "c_text_dy", "c_source", "c_pages", "c_secondary_source_author", "c_url_api", "c_url_homepage", "c_notes", "c_title_alt_chn", "c_created_by", "c_created_date", "c_modified_by", "c_modified_date"]]

#setup url resources
url_get_index_year = 'https://input.cbdb.fas.harvard.edu/basicinformation/'
url_get_last_text_id = 'https://input.cbdb.fas.harvard.edu/textcodes/create'

# setup index for output
textid_idx = 1
title_chn_idx = 2
title_idx = 3
text_type_idx = 5
text_cat_idx = 10
text_dy_idx = 13
source_idx = 14
create_by_idx = 21
create_date_idx = 22

# setup index for input
personid_input_idx = 0
title_chn_input_idx =1
source_input_idx = 2

# get input data
input_list = []
with open("input.csv", "r", encoding="utf-8") as f:
    f_handle = csv.reader(f, delimiter="\t")
    for row in f_handle:
        input_list.append(row)

def get_dy_from_personid(personid, url_get_index_year):
    resp = requests.get(url_get_index_year + personid).json()
    return(str(resp['c_dy']))

def convert_pinyin(string_chn):
    string_chn = re.sub(r"[:：].+", "", string_chn)
    return " ".join([word for word in lazy_pinyin(string_chn)])

# create output data
textid_begin = get_new_textid(url_get_last_text_id)
for row in input_list:
    output_row = [""]*len(output[0])
    textid_begin += 1
    output_row[textid_idx] = textid_begin
    output_row[title_chn_idx] = row[title_chn_input_idx]
    output_row[title_idx] = convert_pinyin(row[title_chn_input_idx])
    output_row[text_type_idx] = "01"
    output_row[text_cat_idx] = "1" if row[title_chn_input_idx][-1] == "集" else "0"
    output_row[text_dy_idx] = get_dy_from_personid(row[personid_input_idx], url_get_index_year)
    output_row[source_idx] = row[source_input_idx]
    output_row[create_by_idx] = "load"
    output_row[create_date_idx] = f"{date.today().year}{str('{:0>2d}'.format(date.today().month))}{str('{:0>2d}'.format(date.today().day))}"
    output.append(output_row)

# output data
with open("output.csv", "w", encoding="utf-8", newline="") as f:
    output_writer = csv.writer(f, delimiter='\t')
    output_writer.writerows(output)
    
print("Finished!")
