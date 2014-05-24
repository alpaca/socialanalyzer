"""
Example Usage of Dynamic Queries
--------------------------------
query = FacebookUser.query.filter(age(age=(20,30)))
query = FacebookUser.query.filter(and_(age(age=(20,30)),sex('m')))
query = FacebookUser.query.filter(and_(age(age=(20,30)),sex('m'),currentcity('evanston')))
query = FacebookUser.query.filter(zipcode('60201'))
query = FacebookUser.query.filter(employer('microsoft'))
query = FacebookUser.query.filter(college('northwestern'))
"""

import csv
from app.models import *
from app.models import db
from sqlalchemy import or_, and_, not_
from datetime import datetime
from dateutil import parser

def sex(sex=None, unknown=False):
    if unknown: filtr = FacebookUser.sex == None
    elif sex=='m': filtr = or_(FacebookUser.sex=="male", FacebookUser.sex=="Male")      
    elif sex=='f': filtr = or_(FacebookUser.sex=="female", FacebookUser.sex=="Female")
    elif sex=='o': 
        filtr = and_(
            FacebookUser.sex!="male", 
            FacebookUser.sex!="Male", 
            FacebookUser.sex!="female", 
            FacebookUser.sex!="Female"
        )
    else: filtr = FacebookUser.sex == sex

    return filtr

def currentcity(city=None, unknown=False):
    if unknown: 
        filtr = FacebookUser.currentcity == None
    else:
        filtr = FacebookUser.currentcity.ilike("%%%s%%" % city)
    return filtr

def hometown(city=None, unknown=False):
    if unknown: 
        filtr = FacebookUser.hometown == None
    else:
        filtr = FacebookUser.hometown.ilike("%%%s%%" % city)
    return filtr

def zipcode(zipcode=None, typeCity=None, unknown=False):
    if unknown:
        filtr = FacebookUser.locations == None
    else:
        filtr = FacebookUser.locations.any(zipcode=zipcode, type=typeCity)

    return filtr

def employer(employer=None, unknown=False):
    if unknown: filtr = FacebookUser.employer == None
    else: filtr = FacebookUser.employer.ilike("%%%s%%" % employer)
    return filtr

def school(school=None, unknown=False):
    if unknown:
        filtr = and_(
            FacebookUser.college == None,
            FacebookUser.highschool == None
        )
    else:
        filtr = or_(
            FacebookUser.college.ilike("%%%s%%" % school),
            FacebookUser.highschool.ilike("%%%s%%" % school),
        )

    return filtr

def college(college=None, unknown=False):
    if unknown: filtr = FacebookUser.college == None
    else: filtr =  FacebookUser.college.ilike("%%%s%%" % college)

    return filtr

def highschool(college=None, unknown=False):
    if unknown: filtr = FacebookUser.highschool == None
    else: filtr = FacebookUser.highschool.ilike("%%%s%%" % highschool)

    return filtr

def likes(unknown=False):
    if unknown: filtr = FacebookUser.pages == None
    else: filtr = FacebookUser.pages != None

    return filtr

def employerInList(employerList=[], unknown=False, opposite=False):
    if employerList == None: employerList = []
    if unknown: filtr = employer(unknown=True)
    elif len(employerList) <1: filtr=None
    elif opposite == False:
        or_list = [employer(x) for x in employerList]
        filtr = or_(*or_list)
    elif opposite == True:  # opposite == True
        and_list = [employer(x) for x in employerList]
        filtr = or_(*and_list)
        filtr = not_(filtr)
        # import pdb; pdb.set_trace()
    return filtr

def currentCityInList(cityList=[], unknown=False, opposite=False):
    if cityList==None: cityList = []
    if unknown: filtr = currentcity(unknown=True)
    elif len(cityList) <1: filtr=None
    elif type(cityList[0]) == int:
        if opposite == False:
            or_list = [zipcode(x, "currentcity") for x in cityList]
            filtr = or_(*or_list)
            return filtr
        elif opposite == True:  # opposite == True
            # just returning all for now, not correct!
            and_list = [zipcode(x, "currentcity") for x in cityList]
            filtr = not_(and_(*and_list))
            return filtr
    else:
        or_list = [currentcity(x) for x in cityList]
        if opposite == False:
            filtr = or_(*or_list)
        elif opposite == True:
            filtr = and_(*or_list)
            filtr = not_(filtr)

        return filtr

def hometownInList(cityList=[], unknown=False):
    if cityList==None: cityList = []
    if unknown: filtr = hometown(unknown=True)
    elif len(cityList) <1: filtr= None
    elif type(cityList[0]) == int:
        or_list = [zipcode(x, "hometown") for x in cityList]
        filtr = or_(*or_list)
    else:
        or_list = [hometown(x) for x in cityList]
        filtr = or_(*or_list)
    return filtr

def highSchoolInList(schoolList=[], unknown=False):
    if schoolList==None: cityList=[]
    if unknown: filtr = highschool(unknown=True)
    elif len(schoolList) <1: filtr= None
    elif type(schoolList[0]) == int:
        or_list = [zipcode(x, "highschool") for x in schoolList]
        filtr = or_(*or_list)
    else:
        or_list = [highschool(x) for x in schoolList]
        filtr = or_(*or_list)
    return filtr

def collegeInList(schoolList=[], unknown=False):
    if schoolList==None: schoolList = []
    if unknown: filtr = college(unknown=True)
    elif len(schoolList) <1: filtr= None
    elif type(schoolList[0]) == int:
        or_list = [zipcode(x, "college") for x in schoolList]
        filtr = or_(*or_list)
    else:
        or_list = [college(x) for x in schoolList]
        filtr = or_(*or_list)
    return filtr


def age(age=[0,10000], unknown=False):
    if age==None: age=[0, 10000]
    if unknown: filtr = FacebookUser.birthday == None
    else:
        min_age = age[0]
        max_age = age[1]        
        tNow = datetime.now()
        filtr = FacebookUser.birthday.between(
                datetime(year=tNow.year-max_age, month=1, day=1), 
                datetime(year=tNow.year-min_age,month=1, day=1)
            )
        filtr2 = collegeInList(map( str , range(2014-max_age+20, 2014-min_age+22)))
        filtr3 = highSchoolInList(map( str , range(2014-max_age+16, 2014-min_age+18)))
        filtr = or_(filtr, filtr2, filtr3)
    
    return filtr

__all__ = ['sex','currentcity','hometown', 'school', 'employer','zipcode', 
           'likes','highschool','college','employerInList','currentCityInList',
           'hometownInList', 'highSchoolInList','collegeInList','age']

###################################################################

# # Examples

# # Example 1
# print "Example 1: Querying people of age 20 to 30"
# query = FacebookUser.query.filter(
#             age(age=(20,30))
#         )
# print map(lambda user: (user.username, user.birthday), query.all())
# print "\n"

# # Example 2
# print "Example 2: Querying people of age 20 to 30 who are male"
# query = FacebookUser.query.filter(
#     and_(
#         age(age=(20,30)),
#         sex(sex='m')
#     )
# )
# print map(lambda user: (user.username, user.birthday, user.sex), query.all())
# print "\n"

# # Example 3
# print "Example 3: Querying people of age 20 to 30 who are male and from evanston"
# query = FacebookUser.query.filter(
#     and_(
#         age(age=(20,30)),
#         sex(sex='m'),
#         city('evanston')
#     )
# )
# print map(lambda user: (user.username, user.birthday, user.sex, user.currentcity, user.hometown), query.all())
# print "\n"

# # Example 4
# print "Example 4: People who have zipcode 60201"
# query = FacebookUser.query.filter(
#     zipcode('60201')
# )
# print map(lambda user: (user.username, map(lambda location: (location.type, location.zipcode) ,user.locations)), query.all())
# print "\n"

# # Example 5
# print "Example 5: People who's employer is microsoft"
# query = FacebookUser.query.filter(
#     employer('microsoft')
# )
# print map(lambda user: (user.username, user.employer), query.all())
# print "\n"

# # Example 6
# print "Example 6: People who's college is Northwestern"
# query = FacebookUser.query.filter(
#     college('northwestern')
# )
# print map(lambda user: (user.username, user.college), query.all())
# print "\n"

# print "------------------------------------------------------------"

# ###################################################################