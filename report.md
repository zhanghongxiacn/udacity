
# OpenStreetMap Data Case Study

## Map Area
Chengdu,Sichuan,China
+ <https://www.openstreetmap.org/node/244077729#map=11/30.6683/104.0776>
+ <https://mapzen.com/data/metro-extracts/metro/chengdu_china/>
This map is one of my favorite city, so I’m more interested to see what database querying reveals, and
I’d like an opportunity to contribute to its improvement on OpenStreetMap.org.

## Problems Encountered in the Map
After initially auditting a small sample size of the Chengdu area by running audit.py file.
I noticed six main problems with the data, which I will discuss in the following order:
+ Overabbreviatedstreet names("Binjiang E Rd")
+ Inconsistent street names("Chengshou St","Jinsi Jie","wenshuyuan st")
+ Incorrect phone number format("(028)87383891","028-85950826","83222271")
+ Incorrect city name("Chengu")
+ Inconsistent city name("Chengdu"、"chengdu"、"成都"、"成都市")
+ Incorrect postal codes(Chengdu area zip codes range from "610000" to "611944",however there is a zip code was "028".)

### Overabbreviated and Inconsistent street names
Spell out all street types ，capitalize the street name and change the "jie" to "Street".

- "Chengshou St" to "Chengshou Street"
- "wenshuyuan st" to "Wenshuyuan Street"
- "Jinsi Jie" to "Jinsi Street"
```python

def update_name(name):
    """
    Clean street name for insertion into SQL database
    """
    #make street name be capitalized 
    first_word = name.rsplit(None, 1)[0]                   
    if first_word.islower():
        print (first_word)
        name = re.sub(first_word, first_word.title(), name)
    
    if name == "Yangjiang Rd., Shuangliu":
        name = "Yangjiang Road, Shuangliu"
        return name
    elif name == "No. 20 Hongxing road 2 section":
        name = "No. 20 Hongxing Road Second Section"
        return name
    elif name == "人民南路四段 - Renminnanlu 4 Duan":
        name = "人民南路四段 - Renmin Road South Fourth Section"
        return name
    elif name == "人民南路二段 - Section 2 Renmin Road South":
        name = "人民南路二段 - Renmin Road South Second Section"
        return name
    else:
        original_name = name
        for key in mapping.keys():
            # Only replace when mapping key match (e.g. "St.") is found at end of name
            type_fix_name = re.sub(r'\s' + re.escape(key) + r'$', ' ' + mapping[key], original_name)
            nesw = nesw_re.search(type_fix_name)
            if nesw is not None:
                for key in street_mapping.keys():
                    # Do not update correct names like St. Clair Avenue West
                    dir_fix_name = re.sub(r'\s' + re.escape(key) + re.escape(nesw.group(0)), " " + street_mapping[key] + nesw.group(0), type_fix_name)
                    if dir_fix_name != type_fix_name:
                        # print original_name + "=>" + type_fix_name + "=>" + dir_fix_name
                        return dir_fix_name
            if type_fix_name != original_name:
                # print original_name + "=>" + type_fix_name
                return type_fix_name
    # Check if avenue, road, street, etc. are capitalized
    last_word = original_name.rsplit(None, 1)[-1] 
    if last_word.islower() or first_word.islower():
        original_name = re.sub(last_word, last_word.title(), original_name)
        original_name = re.sub(first_word, first_word.title(), original_name)
    return original_name
```
### Incorrect phone number format
Convert, where necessary, to international format with spaces: "+86 ### #### ####".

- "(028)87383891" to "+86 028 8738 3891"
- "028-85950826" to "+86 028 8595 0826"
- "83222271" to "+86 028 8322 2271"
- "13880710998" to "+86 13880710998"
```python
PHONENUM = re.compile(r'\+86\s\d{3}\s\d{4}\s\d{4}')
def update_phone_num(phone_num):
    """
    Clean phone number for insertion into SQL database
    """
    # Check for valid phone number format
    m = PHONENUM.match(phone_num)
    if m is None:
        # Convert all dashes to spaces
        if "-" in phone_num:
            phone_num = re.sub("-", "", phone_num)
        # Remove all brackets
        if "(" in phone_num or ")" in phone_num:
            phone_num = re.sub("[()]", "", phone_num)

        # Remove the first two zero
        if re.match(r'^0{2}', phone_num) is not None:
            phone_num = re.sub("^0{2}", "", phone_num)
            
        # Remove all the spaces        
        if " " in phone_num:
            phone_num = re.sub(" ", "", phone_num)  
            
        # Add full country code and spaces   
        length = len(phone_num)
        if re.match(r'^1\d{10}', phone_num) is not None:
            phone_num ="+86 "+phone_num      
        elif length>=8 and length<=14:
            phone_num ="+86 028 "+phone_num[length-8:length-4]+" "+phone_num[length-4:]
 
        # Ignore tag if no area code and local number (<10 digits)
        elif sum(c.isdigit() for c in phone_num) < 10:
            return None
    return phone_num
```
### Inconsistent and “Incorrect” city name
Use "Chengdu" to correct "chengu" and uniform ("成都","成都市","chengdu").
- "chengu" to "Chengdu"
- "chengdu" to "Chengdu"
- "成都“ to "Chengdu"
```python
def update_city(city):
    if city in["成都","成都市","chengdu","Chengu"]:
        city = "Chengdu"
    return city
```
### Incorrect postal codes
After running audit.py file,there is a incorrect post code "028".Through looking for the "city" tag with the same node id,it can make sure that the post code is "610041".
```python
POSTCODE = re.compile(r'\d{6}')
def update_postcode(postcode):
    m = POSTCODE.match(postcode)
    if m is not None:
        return postcode
    else:
        # Fix the zip code revealed in postal code audit 
        if postcode == "028":
            postcode = "610041"
            return postcode   
        # Ignore tag if improper postal code format
        else:
            return None
```
## Data Overview and Additional Ideas

This section contains basic statistics about the dataset, the Sqlite queries used to gather
them, and some additional ideas about the data in context.

### File sizes
```
chengdu_china.osm ......... 52.2 MB
chengdu.db .......... 42.5 MB
nodes.csv ............. 20.6 MB
nodes_tags.csv ........ 0.37 MB
ways.csv .............. 1.92 MB
ways_tags.csv ......... 2.36 MB
ways_nodes.cv ......... 7.05 MB 
```
### Number of nodes
```sql
sqlite> SELECT COUNT(*) FROM nodes;
```
255794
### Number of ways
```sql
sqlite> SELECT COUNT(*) FROM ways;
```
32894
### Number of unique users
```sql
sqlite> SELECT COUNT(DISTINCT(e.uid))
FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) e;
```
545
### Top 10 contributing users
```sql
sqlite> SELECT e.user, COUNT(*) as num
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e
GROUP BY e.user
ORDER BY num DESC
LIMIT 10;
```
```
巴山夜雨|49349
geodreieck4711|18809
katpatuka|18290
hanchao|12934
jamesks|10953
Ernst Poulsen|9085
guanchzhou|8679
jechterhoff|8593
somethingsimple|7201
ff5722|6866
```
### Number of users appearing only once (having 1 post)
```sql
sqlite> SELECT COUNT(*)
FROM (SELECT e.user, COUNT(*) as num
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e
GROUP BY e.user
HAVING num=1) u;
```
118
## Additional Ideas
### Contributor statistics and gamification suggestion
## Additional Data Exploration
### Top 10 appearing amenities
```sql
sqlite> SELECT value, COUNT(*) as num
FROM nodes_tags
WHERE key='amenity'
GROUP BY value
ORDER BY num DESC
LIMIT 10;
```
```
restaurant|165
toilets|71
cafe|62
bank|61
parking|61
school|51
hospital|40
fuel|34
fast_food|25
bicycle_parking|24
```
### Most popular cuisines
```sql
sqlite> SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags
JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='restaurant') i
ON nodes_tags.id=i.id
WHERE nodes_tags.key='cuisine'
GROUP BY nodes_tags.value
ORDER BY num DESC
LIMIT 10;
```
```
```
### First contribution
```sql
sqlite> SELECT timestamp FROM Nodes UNION SELECT timestamp From Ways
        ORDER BY timestamp
        LIMIT 1;
```
2008-05-17T21:26:53Z


## Conclusion
The Chengdu OpenStreetMap dataset is a quite messy. While it is clear that the data is not 100% clean, I believe it was sufficiently cleaned for the purposes of this project. Via SQL query, I learned a few new things about Chengdu. The dataset is very useful, though areas for improvement exist.
