<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" >
<head>


    <link rel="stylesheet" href="/static/css/micro/blueprint/screen.css" type="text/css" media="screen, projection, print"/>
    <!--[if lt IE 8]> 
    <link rel="stylesheet" href="/static/css/micro/blueprint/ie.css" type="text/css" media="screen, projection"/>
    <![endif]-->
    <link rel="stylesheet" href="/static/css/micro/typography.css" type="text/css" media="screen, projection, print"/>
    <link rel="stylesheet" href="/static/datepicker/css/datepicker.css" type="text/css" />

    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>

    <script type="text/javascript" src="/static/datepicker/js/datepicker.js"></script>
    <script type="text/javascript" src="/static/datepicker/js/eye.js"></script>
    <script type="text/javascript" src="/static/datepicker/js/layout.js"></script>

<style>
th {padding:0px 0px 0px 0px;}
</style>

</head>

<body>  

<?python
import calendar
from hubspace.utilities.uiutils import now
import hubspace.utilities.date as dateutils
from hubspace.model import RUsage

rightnow = RUsage.get(booking_id).start

def day_ext(day):
    if day == 1: return 'st'
    elif day == 2: return 'nd'
    elif day == 3: return 'dd'
    else: return 'th'

day_tuples = [(calendar.day_abbr[i],i) for i in range(7)]
today_weekday = rightnow.weekday()
today_weekday_str = calendar.day_name[rightnow.weekday()]
today_str = '%d/%d/%d' % (rightnow.month, rightnow.day, rightnow.year)
today_day_str = str(rightnow.day)+day_ext(rightnow.day)
today_weekday_week_no =  dateutils.find_week_no(rightnow)
today_weekday_week_no_str =  str(today_weekday_week_no) + day_ext(today_weekday_week_no)
?>

<script>
$(document).ready(function() {
    var hide_all_opts = function () {
        $('#daily_opts').hide();
        $('#weekly_opts').hide();
        $('#monthly_opts').hide();
        $('#yearly_opts').hide();
        $('#multidate_opts').hide();
        $('#repeat_dates_opts').hide();
    };

    var show_daily_opts = function () {
        hide_all_opts();
        $('#daily_opts').show();
        select_daily_opt_every();
        show_repeat_dates();
    };
    var show_weekly_opts = function () {
        hide_all_opts();
        $('#weekly_opts').show();
        show_repeat_dates();
        select_weekly_opt_repeat_days();
    };
    var show_monthly_opts = function () {
        hide_all_opts();
        $('#monthly_opts').show();
        show_repeat_dates();
        set_monthly_opt_preview();
    };
    var show_multidate_opts = function () {
        hide_all_opts();
        $('#multidate_opts').show();
        $('#multidate_calendar').show();
    };

    var show_repeat_dates = function () {
        $('#repeat_dates_opts').show();
    };

    var get_repeat_dates_str = function () {
        var date_start = $('#date_start').DatePickerGetDate().toDateString();
        var date_end   = $('#date_end').DatePickerGetDate().toDateString();
        return " from " + date_start + " to " + date_end;
    };

    var select_daily_opt_every = function () {
        $('#preview').text("Repeat every '" + $('#daily_opt_every').val() + "' day(s) " + get_repeat_dates_str());
    };
    var set_monthly_opt_preview = function () {
        var monthly_opt_val = $('.monthly_opt_day:checked').val();
        if (monthly_opt_val == 'weekday') {
            $('#preview').text("Every " + "${today_weekday_week_no_str}" + " ${today_weekday_str}" + " of month" + get_repeat_dates_str());
        } else if (monthly_opt_val == 'day') {
            $('#preview').text("Every " + "${today_day_str}" + " day of the month" + get_repeat_dates_str());
        } else if (monthly_opt_val == 'end') {
            $('#preview').text("Last day of the month" + get_repeat_dates_str());
        };
    };
    var select_weekly_opt_repeat_days = function () {
        var all_days = [];
        var val = '';
        $('[name=weekly_opt_repeat_days]:checked').each(function(i, Element) {
            val += $(this).val() + ' ';
        });
        $('#preview').text("Every " + val + " of week " + get_repeat_dates_str());
    };
    var init = function () {
        $('#date_start').DatePicker({
            format: 'm/d/Y',
            date: ${"'%s'" % today_str},
            position: 'right',
            calendars: 1,
            //view: 'months',
            onChange: function(formated, dates){
                $('#date_start').val(formated);
                $('#date_start').DatePickerHide();
            }
        });
        $('#date_end').DatePicker({
            format: 'm/d/Y',
            date: ${"'%s'" % today_str},
            position: 'right',
            calendars: 1,
            //view: 'months',
            onChange: function(formated, dates){
                $('#date_end').val(formated);
                $('#date_end').DatePickerHide();
            },
           onRender: function(date){
               var date_array = new Array();
               date_array = $('#date_start').val().split('/');
               var date_start = new Date(date_array[2], date_array[0]-1, date_array[1]); // Javascript months starts with 0
               return {
                       disabled: (date_start.valueOf() > date.valueOf()) // Dont use less than sign here. It will not work, thanks to kid processing
                    }
           }
        });

        $('#multidate_calendar').DatePicker({
            date: ${"'%s'" % today_str},
            flat: true,
            format: 'm/d/Y',
            calendars: 2,
            starts: 1,
            mode: 'multiple',
            onChange: function(formated, dates){
                var dates_str = '<ol>';
                for (var i in dates) {
                    dates_str += '<li>' + dates[i].toDateString() + '</li>';
                };
                dates_str += '</ol>';
                $('#preview').html('<br/>On following dates: ' + dates_str);
                $('#repeat_dates').val(formated);
            }
        });

        $('#monthly').click( show_monthly_opts );
        $('#daily').click( show_daily_opts );
        $('#weekly').click( show_weekly_opts );
        $('#multidate').click( show_multidate_opts );

        $('#daily_opt_every').keyup( select_daily_opt_every );
        $('input[name=weekly_opt_repeat_day]').click( select_weekly_opt_repeat_days );

        $('.monthly_opt_day').click( set_monthly_opt_preview );
        $('#monthly_opt_day_day').keyup( set_monthly_opt_preview );

        $('#save').click( function () {
            var data = $("#repeat_booking").serializeArray();
            $.ajax({
                url: "/addRecurringEvent",
                type: 'POST',
                data: data,
                beforeSend: function () {
                    $('#preview').text('processing...');
                    $('#repeat_conf').hide();
                    $('#save').hide();
                    $('#notify_member').hide();
                },
                success: function (data) {
                    $('#preview').html('<span>' + data + '</span>');
                }
            });
        });

        $('#monthly').click();
    };

    init();
});
</script>

<h4 class="box">Add Bookings </h4>

<form id="repeat_booking">

<input type="hidden" name="booking_id" value="${booking_id}"/>

<div class="container" id="repeat_conf">

<div class="span-4 border left">
    <br/>
    <strong>
    <input type="radio" name="pattern" value="daily" id="daily" title="Daily"/>Daily <br/>
    <input type="radio" name="pattern" value="weekly" id="weekly"/>Weekly <br/>
    <input type="radio" name="pattern" value="monthly" id="monthly"/>Monthly <br/>
    <input type="radio" name="pattern" value="multidate" id="multidate"/>Multiple dates<br/>
    </strong>
</div>
<div id="options_area" class="span-9 colborder last">
    <br/>
    <div id="repeat_dates_opts" class="span-9 last">
        <dl>
        <dt>Dates range:</dt>
        <hr/>
        <dd>
            <div class="span-5">
                <div class="span-2"> Start from: </div>
                <div class="span-3 last"> <input type="text" name="from_date" id="date_start" value="${today_str}"/>(mm/dd/yyyy) </div>
                <div class="span-5 last"> &nbsp; </div>
                <div class="span-2"> Till: </div>
                <div class="span-3 last"> <input type="text" name="to_date" id="date_end" value="${today_str}"/>(mm/dd/yyyy) </div>
                <div class="span-5 last"> &nbsp; </div>
            </div>
        </dd>
        </dl>
        <hr/>
    </div>

    <div id="daily_opts">
        Repeat every <input type="text" name="daily_opt_every" id="daily_opt_every" size="2" value="1"/> day(s)
    </div>
    <div id="weekly_opts">
        Repeat every weekday<br/>
        <input type="checkbox" name="weekly_opt_repeat_days" py:for="day_tuple in day_tuples" py:attrs="day_tuple[1] == today_weekday and {'checked':'checked'} or {}" value="${day_tuple[0]}"> ${day_tuple[0]} </input>
    </div>
    <div id="monthly_opts">
        <input type="radio" name="monthly_opt_day" value="end"/>Last day of every month<br/>
        <input type="radio" name="monthly_opt_day" class="monthly_opt_day" py:attrs="{'checked':'checked'}" value="day"/>By date of the month: <input type="text" value="${rightnow.day}" name="monthly_opt_day_day" id="monthly_opt_day_day" size="2" maxlength="2"/>
        <br/>
        <input type="radio" name="monthly_opt_day" class="monthly_opt_day" value="weekday"/>By day of the week:
            ${today_weekday_week_no_str} ${today_weekday_str}
        <input type="hidden" name="monthly_opt_weekday_day" value="${today_weekday}"/>
        <input type="hidden" name="monthly_opt_weekday_week_no" value="${today_weekday_week_no}"/>
        <!--
        - <input type="checkbox" id="monthly_opt_weekday_day" name="monthly_opt_weekday_day" py:for="day_tuple in day_tuples" py:attrs="day_tuple[1] == today_weekday and {'checked':'checked'} or {}" value="${day_tuple[0]}"> ${day_tuple[0]} </input><br/>
        - <input type="text" value="1" name="" id="monthly_opt_weekday_week_no" size="1" maxlength="1"/> week 
        -->
    </div>
    <div id="multidate_opts">
        Choose multiple dates
        <div id="multidate_calendar"/>
        <input type="hidden" name="repeat_dates" id="repeat_dates"/>
    </div>
</div>

</div>

<div class="container">
    <div class="span-13 prepend-1 colborder last">
    <br/>
        <hr/>
        <p><strong>Summary: </strong><br/><span id="preview"/></p>
        <hr/>
        <c id="notify_member"><input type="checkbox" name="notify_member" value="1"/> Notify member<br/></c>
        <input type="button" id="save" value="Submit"/>
    </div>
</div>

</form>

</body>

</html>
