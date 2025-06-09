# Copyright (c) 2024, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PrimaryTargetIncentive(Document):
	def before_save(self):
		self.total_payout = 0
		calculate_primary_target_payout(self)
		calculate_collection_target_payout(self)
		calculate_liquid_target_payout(self)
			
def calculate_primary_target_payout(self):
	if self.primary_percentage < 90:
		return

	incentive_settings = frappe.get_single("Primary Target Incentive Settings")
	wet_percent = incentive_settings.primary

	if self.primary_percentage <= 120:
		ep = incentive_settings.incentive_slab_1_on_120_primary
	elif self.primary_percentage <= 150:
		ep = incentive_settings.incentive_slab_2_on_150_primary
	elif self.primary_percentage <= 200:
		ep = incentive_settings.incentive_slab_3_on_200_primary
	else:
		ep = incentive_settings.maximum_earning_potential_in_a_month

	self.primary_ep = ep
	self.primary_wet_percent = wet_percent
	self.primary_payout_amt = (wet_percent / 100) * ep
	self.total_payout += (wet_percent / 100) * ep

def calculate_collection_target_payout(self):
	if self.collection_percentage < 90:
		return

	incentive_settings = frappe.get_single("Primary Target Incentive Settings")
	wet_percent = incentive_settings.collection_90_of_primary

	if self.collection_percentage <= 120:
		ep = incentive_settings.incentive_slab_1_on_120_primary
	elif self.collection_percentage <= 150:
		ep = incentive_settings.incentive_slab_2_on_150_primary
	elif self.collection_percentage <= 200:
		ep = incentive_settings.incentive_slab_3_on_200_primary
	else:
		ep = incentive_settings.maximum_earning_potential_in_a_month

	self.collection_ep = ep
	self.collection_wet_percent = wet_percent
	self.collection_payout_amt = (wet_percent / 100) * ep
	self.total_payout += (wet_percent / 100) * ep

def calculate_liquid_target_payout(self):
	if self.liquid_percentage < 90:
		return

	incentive_settings = frappe.get_single("Primary Target Incentive Settings")
	wet_percent = incentive_settings.focus_drive_liquid_30_of_primary

	if self.liquid_percentage <= 120:
		ep = incentive_settings.incentive_slab_1_on_120_primary
	elif self.liquid_percentage <= 150:
		ep = incentive_settings.incentive_slab_2_on_150_primary
	elif self.liquid_percentage <= 200:
		ep = incentive_settings.incentive_slab_3_on_200_primary
	else:
		ep = incentive_settings.maximum_earning_potential_in_a_month

	self.liquid_ep = ep
	self.liquid_wet_percent = wet_percent
	self.liquid_payout_amt = (wet_percent / 100) * ep
	self.total_payout += (wet_percent / 100) * ep
