<?python
from hubspace.model import User, Resource
from datetime import datetime
from hubspace.utilities.uiutils import oddOrEven, print_error, now
from hubspace.validators import dateconverter
odd_or_even = oddOrEven().odd_or_even

def date(object):
    if isinstance(object, Resource):
        date = now(object.place)
    elif object.date:
        date = object.date
    return dateconverter.from_python(date)

def cost(object):
    if isinstance(object, Resource):
        return ''
    elif object.customcost:
        return object.customcost

def quantity(object):
    if isinstance(object, Resource):
        return '1'
    elif object.quantity:
        return object.quantity

def name(object):
    if isinstance(object, Resource):
        return _('custom')
    elif 'customname' in object:
        return object.customname

def type(object):
    if isinstance(object, Resource):
        return object.type
    elif 'temp_id' in object:
        return Resource.get(object.temp_id).type

start = 9
end = 23
def hours():
    return range(start, end)

def add_zero(hour):
    if len(str(hour))==1:
        return "0"+str(hour)
    return str(hour)

#XXX this needs to use datetime format in order to be internationalisable
def display_hour(hour):
    return add_zero(hour) 

tg_errors = None

def start_hour(object, hour):
    if isinstance(object, Resource):
       return {}
    if object.start and object.start.hour==hour:
        return {'selected':'selected'}
    return {}

def start_minute(object, minute):
    if isinstance(object, Resource):
       return {}
    if object.start.minute and object.start.minute==minute:
        return {'selected':'selected'}
    return {}

def end_hour(object, hour):
    if isinstance(object, Resource):
       return {}
    if object.end_time and object.end_time.hour==hour:
        return {'selected':'selected'}
    return {}

def end_minute(object, minute):
    if isinstance(object, Resource):
       return {}
    if object.end_time and object.end_time.minute==minute:
        return {'selected':'selected'}
    return {}
?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
  <div class="dataBox">
<div class="dataBoxContent">
     <table class="addRusageTable data detailTable" cellpadding="" cellspacing="0">
         <tr class="${odd_or_even()}">
             <td class="line">
                 Billed User
             </td>
             <td>
             <select name="user">
		        <option py:attrs="{'value':user}" py:content="User.get(int(user)).display_name"></option>
		        <option py:for="bill_user in [bill_user for bill_user in User.get(int(user)).billed_for if bill_user!=User.get(int(user))]" py:attrs="{'value':bill_user.id}" py:content="bill_user.display_name"></option>
	      </select>
             </td>
         </tr>
         <tr class="${odd_or_even()}">
           <td class="line">
           Date:</td><td><a id="display_rusage_date" style="cursor:pointer;">${date(object)} <img src="/static/images/booking_down.png" /></a>
           <input id="date" name="date" type="text" class="invisible_input" style="margin-left:-140px;" value="${date(object)}"/> 
            <div class="errorMessage" py:if="tg_errors">${print_error('date', tg_errors)}</div>
             </td>
         </tr>
             <c py:if="object.time_based" py:strip="True">
               <tr class="${odd_or_even()}">
 		  <td class="line">
                 	Start time:
                  </td><td>
                    <select id="start.hour" name="start.hour">
		          <option py:for="hour in hours()" py:attrs="start_hour(object, hour)">${display_hour(hour)}</option>
		    </select>:
                    <select id="start.minute" name="start.minute" >
		        <option py:attrs="start_minute(object, 0)">00</option>
		        <option py:attrs="start_minute(object, 15)">15</option>
                        <option py:attrs="start_minute(object, 30)">30</option>
		        <option py:attrs="start_minute(object, 45)">45</option>
		    </select>
                    <div class="errorMessage" py:if="tg_errors">${print_error('start', tg_errors)}</div>
             </td>
               </tr>
               <tr class="${odd_or_even()}"> 
                   <td class="line">End time:</td><td>                   <select id="end.hour" name="end.hour">
		       <option py:for="hour in hours()" py:attrs="end_hour(object, hour)">${display_hour(hour)}</option>
		   </select>:
                   <select id="end.minute" name="end.minute" >
		        <option py:attrs="end_minute(object, 0)">00</option>
		        <option py:attrs="end_minute(object, 15)">15</option>
                        <option py:attrs="end_minute(object, 30)">30</option>
		        <option py:attrs="end_minute(object, 45)">45</option>
		    </select>
                    <div class="errorMessage" py:if="tg_errors">${print_error('end', tg_errors)}</div>
	     </td>
 
               </tr>
             </c>
             <c py:if="not object.time_based" py:strip="True">

                <tr class="${odd_or_even()}">
 		  <td class="line">
                     Time of Usage:
                  </td><td>
                    <select id="start.hour" name="start.hour">
		          <option py:for="hour in hours()">${display_hour(hour)}</option>
		    </select>:
                    <select id="start.minute" name="start.minute" >
		        <option>00</option>
		        <option>15</option>
                        <option>30</option>
		        <option>45</option>
		    </select>
                    <div class="errorMessage" py:if="tg_errors">${print_error('start', tg_errors)}</div>
             </td>
                </tr>
                <tr class="${odd_or_even()}">
                   <td class="line">
                      Quantity: 
                   </td><td><input type="text" name="quantity" value="${quantity(object)}" />
       <div class="errorMessage" py:if="tg_errors">${print_error('quantity', tg_errors)}</div>
             </td>
                </tr>
             </c>
             <tr py:if="type(object)=='custom'" class="${odd_or_even()}">
               <td class="line">
                  Custom billing name:
               </td><td><input type="text" name="customname" value="${name(object)}" />
               <div class="errorMessage" py:if="tg_errors">${print_error('customname', tg_errors)}</div>
               </td>
             </tr>
             <tr class="${odd_or_even()}">
               <td class="line">
                 Cost (leave blank for automatic cost): 
               </td><td><input type="text" name="customcost" value="${cost(object)}" />
       <div class="errorMessage" py:if="tg_errors">${print_error('customcost', tg_errors)}</div>
               </td>
             </tr>
             <input type="button" id="${User.get(int(user)).id}_submit_add_rusage" value="${_('submit')}" />
             <input type="button" id="${User.get(int(user)).id}_cancel_add_rusage" value="${_('cancel')}" />
    </table>
  </div>
 </div>
</div>   


