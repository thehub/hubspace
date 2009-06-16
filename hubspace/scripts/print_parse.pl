#!/usr/bin/perl

##################################################################
# Configuration settings
#
# $place is the id for the hub from the space management system
# 1 == London
# 2 == Bristol
# 3 == 
my $place = 1;

# $log_file is the location of the printer log file
my $log_file = 'http://hublondon:hublondon\@192.168.1.238/jobacct.dat';

my $username = 'webapi';
my $password = 'test';

my $success_log = '/var/backup/print_parse/success.log';
my $no_alias_log = '/home/jonathan.robinson/unknown_aliases.txt';

# %resource_types stores a lookup to tell us which resource type we should use - this should be done dynamically
my %resource_types = (
             'A4'  => { 'colour' => 'A4Colour', 'bw' => 'A4BW'},
             'A3'  => { 'colour' => 'A3Colour', 'bw' => 'A3BW'}
             );

my $server = 'http://members.the-hub.net/';

##################################################################
# Variable declarations
##################################################################
use strict;
use warnings;
use Data::Dumper;
use Text::CSV;
use Date::Parse;
use Date::Format;
use LWP;
use LWP::Simple;

my %users;
my %unknown_users;
my @already_submitted;
my $job_id;
my $job_name;
my $date;
my $line;
my @line_arr;
my $print_username;
my $pages;
my $page_size;
my $C;
my $M;
my $Y;
my $K;
my $colours;
my $resource;
my $user;
my $start;
my $quantity;
my $success_counter = 0;

my $csv = Text::CSV->new();
my $browser = LWP::UserAgent->new;
#open (ALL_JOBS_FILE, ">>$all_jobs_log");
#open (NO_ALIAS_FILE, ">$no_alias_log");

##################################################################
# Download print logs, alias lists and resource lists and check validity
##################################################################
print "Get alias list\n";
my $response = $browser->post(
	"${server}alias_list?location=1",
	[
		'user_name' => $username, 
		'password' => $password, 
		'login' => 'Login'
	]
);

my @alias_list = split('\r', $response->content);

print "Get job list\n";
$browser->credentials(
    '192.168.1.238:80',
    'Manage Job Accounting',
    'hublondon' => 'hublondon'
  );
my $job_list_in = $browser->get($log_file);
my @job_list = split('\n', $job_list_in->content);


##################################################################
# Process the alias list to build a hash
##################################################################
print "Process alias list\n";
foreach $line (@alias_list){
	$line = trim($line);
	if ($csv->parse($line)) {
		my @columns = $csv->fields();
		
		#remove 1st value to use as user id
		my $user_id = shift(@columns);
		
		foreach my $user (@columns){
			$users{$user} = $user_id;
		}
	}
}

##################################################################
# get a list of successful print jobs already submitted
##################################################################
print "Check jobs already submitted\n";
open(FILE,$success_log) or die "Can't open $success_log:$!\n";
while (<FILE>){
	chomp();
	my ($log_in) = split(/ /);
	print $log_in;
	if(trim($log_in) ne 'Job Index'){
		@already_submitted[trim($log_in)] = 1;
	}
}
close(FILE);

##################################################################
# Process the print logs
##################################################################
print "Process logs\n";
open (SUCCESS_FILE, ">>$success_log");

foreach $line (@job_list){
	process_line($line);
	if($job_id ne 'Job Index'){
		if(!exists $already_submitted[$job_id]){
			if(exists $users{$print_username}){
				if(exists $resource_types{$page_size}->{$colours}){
					$resource = $resource_types{$page_size}->{$colours};
				}else{
					$resource = $resource_types{'A4'}->{'bw'};
				}
				$user = $users{$print_username};
				
				if($date < 1167609600){
					$start = time2str("%d %B %Y %H:%M:%S", 1167609600);
				}else{
					$start = time2str("%d %B %Y %H:%M:%S", $date);
				}
				
				$quantity = $pages;
				my $description = "Print job no: $job_id - name: $job_name";
				my $request = "/book_print_resource/$page_size$colours/$place/" . url_encode($description) . "?start_datetime=" . url_encode($start) . "&quantity=$quantity&user=$user";
				if(make_request($request)){
					#add line to processed log
					$success_counter++;
					print SUCCESS_FILE $line . "\n";
				}
				
			}else{
				$unknown_users{$print_username} .= $job_name . ',  ';
			}
		}
	}
}

open (NO_ALIAS_FILE, ">$no_alias_log");
foreach my $unknown_user (keys %unknown_users){
	print NO_ALIAS_FILE $unknown_user . ' -------------> ' . $unknown_users{$unknown_user} . "\n";
}

print $success_counter . ' print jobs successfully added';

exit;

sub make_request {
	my $request = shift;
	
	my $response = $browser->post(
		"${server}/$request ",
		[
			'user_name' => $username, 
			'password' => $password, 
			'login' => 'Login'
		]
	);
    
    if($response->content eq 'success'){
    	return 1;
    }else{
    	print $response->content . "\n";
    	return 0;
    }
}

sub process_line {
	my $line = shift;
	@line_arr = split(/\t/,$line);
	$job_id = 	trim($line_arr[0]);
	$print_username = 	trim($line_arr[2]) . '@' . trim($line_arr[3]);
	$job_name = 	trim($line_arr[4]);
	$pages = 		trim($line_arr[6]);
	$date = 		str2time(trim($line_arr[8]));
	$page_size =	trim($line_arr[12]);
	$C =			trim($line_arr[13]);
	$M =			trim($line_arr[14]);
	$Y =			trim($line_arr[15]);
	$K =			trim($line_arr[16]);
	
	if($C eq "0.000000%" && $M eq "0.000000%" && $Y eq "0.000000%"){
		$colours = 'BW';
	}else{
		$colours = 'Colour';
	}
	
}

sub trim {
    my $string = shift;
    for ($string) {
        s/^\s+//;
        s/\s+$//;
    }
    return $string;
}

sub url_encode {
	my $string = shift;
	$string =~ s/([^A-Za-z0-9])/sprintf("%%%02X", ord($1))/seg;
    return $string;
} 
