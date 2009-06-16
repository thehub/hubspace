#!/usr/bin/perl

##################################################################
# Configuration settings
#
# $place is the id for the hub from the space management system
# 1 == London
# 2 == Bristol
# 3 == Johannesburg
# 4 == Bombay
# 5 == Sao Paulo

my $place = 2;

# $user and $pass are the username and password to use to log in to the server
my $user = 'salfield';
my $pass = 'boo';

# $user_group is the group ID to assign all hub users to (this should be created on the server in advance)
my $user_group = 100;

# $home_path is the path to the user's home directories (include a trailing slash)
my $home_path = '/home/';

# $default_shell does what it says on the tin
my $default_shell = '/bin/bash';

# $backup_location is where the existing password files get backed up to
my $backup_location = './backup/';

##################################################################
# Variable declarations
##################################################################
use strict;
use warnings;
use Text::CSV;
use Sort::Key::Natural qw(natsort);
use POSIX 'strftime';
use File::Copy;
use Data::Dumper;

my $csv = Text::CSV->new();

my $passwd_file_new = "";
my $shadow_file_new = "";
my $smbpasswd_file_new = "";

my $passwd_file = "./out/passwd";
my $shadow_file = "./out/shadow";
my $smbpasswd_file = "./out/smbpasswd";

my %passwd_existing;
my %shadow_existing;
my %temp_shadow_existing;
my %smbpasswd_existing;

##################################################################
# Download user list and check validity
##################################################################
my @remote_user_list = `curl -s -F "user_name=$user" -F "password=$pass" -F "login=Login" http://members.the-hub.net/user_list?place=$place`;

if(substr($remote_user_list[0], 0, 2) eq '<!'){
	die "error receiving file\n";
}
if ($csv->parse($remote_user_list[0])) {
	my $columns = $csv->fields();
	if($columns != 6){
		die "This file doesn't look like it's correctly formatted\n";
	}
}

##################################################################
# Extract existing system users from server
##################################################################
open(FILE,$shadow_file) or die "Can't open $shadow_file:$!\n";
while (<FILE>){
	chomp();
	my @shadow_in = split(/:/);
	@temp_shadow_existing{$shadow_in[0]} = \@shadow_in;
}
close(FILE);

open(FILE,$passwd_file) or die "Can't open $passwd_file:$!\n";
while (<FILE>){
	chomp();
	my @passwd_in = split(/:/);
	if($passwd_in[2] < 500){
		@passwd_existing{$passwd_in[2]} = \@passwd_in;
		@shadow_existing{$passwd_in[2]} = @temp_shadow_existing{$passwd_in[0]};
	}
}
close(FILE);

open(FILE,$smbpasswd_file) or die "Can't open $smbpasswd_file:$!\n";
while (<FILE>){
	chomp();
	my @smbpasswd_in = split(/:/);
	if($smbpasswd_in[1] < 500){
		@smbpasswd_existing{$smbpasswd_in[1]} = \@smbpasswd_in;
	}
}
close(FILE);

##################################################################
# Create new files
##################################################################
foreach my $key (natsort (keys(%passwd_existing))) {
	if($shadow_existing{$key}){
		if(!exists($passwd_existing{$key}[6])){$passwd_existing{$key}[6] = '';}
		$passwd_file_new .= $passwd_existing{$key}[0] . ":" . $passwd_existing{$key}[1] . ":" . $passwd_existing{$key}[2] . ":" . $passwd_existing{$key}[3] . ":" . $passwd_existing{$key}[4] . ":" . $passwd_existing{$key}[5] . ":" . $passwd_existing{$key}[6] . "\n";
		$shadow_file_new .= $shadow_existing{$key}[0] . ":" . $shadow_existing{$key}[1] . ":" . $shadow_existing{$key}[2] . ":" . $shadow_existing{$key}[3] . ":" . $shadow_existing{$key}[4] . ":" . $shadow_existing{$key}[5] . ":::\n";
	}
}

foreach my $key (natsort (keys(%smbpasswd_existing))) {
	if(!exists($smbpasswd_existing{$key}[6])){$smbpasswd_existing{$key}[6] = '';}
	$smbpasswd_file_new .= $smbpasswd_existing{$key}[0] . ":" . $smbpasswd_existing{$key}[1] . ":" . $smbpasswd_existing{$key}[2] . ":" . $smbpasswd_existing{$key}[3] . ":" . $smbpasswd_existing{$key}[4] . ":" . $smbpasswd_existing{$key}[5] . ":" . $smbpasswd_existing{$key}[6] . "\n";
}

foreach my $line (@remote_user_list){
	if ($csv->parse($line)) {
		my @columns = $csv->fields();
		$passwd_file_new .= "$columns[0]:x:$columns[2]:$user_group:$columns[1]:$home_path$columns[0]:$default_shell\n";
		$shadow_file_new .= "$columns[0]:$columns[3]:13364:0:99999:7:::\n";
		$smbpasswd_file_new .= "$columns[0]:$columns[2]:$columns[4]:$columns[5]:[U          ]:LCT-44D313E2:\n";
	} else {
		my $err = $csv->error_input;
		print "Failed to parse line: $err";
	}
}

##################################################################
# Compare to existing files to see if we should write them out
##################################################################
my $modified = 0;
my $content;

open INPUT, "<$passwd_file";
undef $/;
$content = <INPUT>;
close INPUT;
$/ = "\n";     #Restore for normal behaviour later in script
if($content ne $passwd_file_new){
	print "passwd file modified\n";
	$modified = 1;
}

open INPUT, "<$shadow_file";
undef $/;
$content = <INPUT>;
close INPUT;
$/ = "\n";     #Restore for normal behaviour later in script
if($content ne $shadow_file_new){
	print "shadow file modified\n";
	$modified = 1;
}

open INPUT, "<$smbpasswd_file";
undef $/;
$content = <INPUT>;
close INPUT;
$/ = "\n";     #Restore for normal behaviour later in script
if($content ne $smbpasswd_file_new){
	print "smbpasswd file modified\n";
	$modified = 1;
}

if(!$modified){
	print "no files modified\n";
	exit;
}

##################################################################
# Double check that we at least have a root user in there
##################################################################
if(substr($passwd_file_new, 0, 22) ne 'root:x:0:0:root:/root:' || substr($shadow_file_new, 0, 5) ne 'root:'){
	die "root does not exist\n";
}

##################################################################
# Back up existing files
##################################################################
my $time = strftime( "%Y%m%d%H%M%S", localtime(time));
mkdir $backup_location . $time;

copy($passwd_file, $backup_location . $time);
copy($shadow_file, $backup_location . $time);
copy($smbpasswd_file, $backup_location . $time);

##################################################################
# Write out files to correct locations
##################################################################
open(DAT,">$passwd_file") || die("Cannot Open File");
print DAT $passwd_file_new; 
close(DAT);

open(DAT,">$shadow_file") || die("Cannot Open File");
print DAT $shadow_file_new; 
close(DAT);

open(DAT,">$smbpasswd_file") || die("Cannot Open File");
print DAT $smbpasswd_file_new; 
close(DAT);

##################################################################
# file format references
##################################################################
# passwd:
# bjpirt:x:501:100:Ben Pirt:/mnt/storage/home/bjpirt:/bin/bash
# bjpirt:x:501:100:Ben Pirt:/mnt/storage/home/bjpirt:/bin/bash

# shadow:
# bjpirt:$1$Tnqb1SsX$P4CAsr.mrsuwlu9HpNUjj0:13364:0:99999:7:::
# bjpirt:$1$Tnqb1SsX$P4CAsr.mrsuwlu9HpNUjj0:13364:0:99999:7:::

# smbpasswd:
# bjpirt:501:81867B7F883635B77C3113B4A1A5E3A0:D44B1AA0C8D99A218CEE877E2FD1BE6C:[U          ]:LCT-44D313E2:
# bjpirt:501:81867B7F883635B77C3113B4A1A5E3A0:D44B1AA0C8D99A218CEE877E2FD1BE6C:[U          ]:LCT-44D313E2: 
