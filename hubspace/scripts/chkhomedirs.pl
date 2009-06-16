#!/usr/bin/perl

##################################################################
# Configuration settings
#
# $place is the id for the hub from the space management system
# 1 == London
# 2 == Bristol
# 3 == 
my $passwd_file = "./out/passwd";

# $home_path is the path to the user's home directories (include a trailing slash)
my $home_path = '/mnt/storage/home/';

# $group_id is the root group's id
my $groupid = 0;

##################################################################
# Parse through the passwd file
##################################################################

open(FILE,$passwd_file) or die "Can't open $passwd_file:$!\n";

while (<FILE>){
	chomp();
	my @passwd_in = split(/:/);
	if($passwd_in[2] > 500){
		my $user = $passwd_in[0];
		my $userid = $passwd_in[2];
		my $homedir = $passwd_in[5];
		#make sure the home dir is in the correct location
		if($home_path . $user ne $homedir){
			# the home dir is in the wrong place
			print "wrong homedir for $user\n";
		}else{
			#create dirctory if necessary
			if(! -d $homedir){
				mkdir('.' . $homedir, 0750);
			}
			#then set permissions
			system "chmod -R 750 $homedir ";
			system "chown -R $userid:$groupid $homedir\n";
		}
	}
}