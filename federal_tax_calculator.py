import pandas
import numpy
import matplotlib
import os
import math


def clear_terminal():
    os.system('cls' if os.name =='nt' else 'clear')


def federal_tax_calculator(taxable_income):


    standard_deduction = 14600
    taxable_income = taxable_income - standard_deduction


    if taxable_income <= 0:
        print("you don't make enough money to pay taxes, federal taxes due:$0.00")
    elif taxable_income <= 11600:
        federal_taxes_owed = taxable_income * 0.1
        print("10% tax bracket, taxes owed: $" + str(federal_taxes_owed))

    elif taxable_income > 11600 and taxable_income <=47150:
        federal_taxes_owed = 1160 + ((taxable_income - 11600)*(0.12))
        print("12% tax bracket, taxes owed: $" + str(federal_taxes_owed))

    elif taxable_income > 47150 and taxable_income <=100525:
        federal_taxes_owed = 1160 + 4266 + ((taxable_income - 47150) * (0.22))
        print("22% tax bracket, taxes owed: $" + str(federal_taxes_owed))

    elif taxable_income >= 100526 and taxable_income <=191950:
        federal_taxes_owed = 1160 + 4266 + 11742.5 + ((taxable_income - 100525) *  (0.24))
        print("24% tax bracket, taxes owed: $" + str(federal_taxes_owed))

    elif taxable_income >= 191951 and taxable_income <= 243725:
        federal_taxes_owed = 1160 + 4266 + 11742.5 + 21942 + ((taxable_income - 191950) * (0.32))
        print("32% tax bracket, taxes owed: $" + str(federal_taxes_owed))

    elif taxable_income >= 243726 and taxable_income <= 609350:
        federal_taxes_owed = 1160 + 4266 + 11742.5 + 21942 + 16568 + ((taxable_income - 243725) * (0.35))
        print("35% tax bracket, taxes owed: $" + str(federal_taxes_owed))

    elif taxable_income >= 609351:
        federal_taxes_owed = 1160 + 4266 + 11742.5 + 21942 + 16568 + 127968.75 + ((taxable_income - 609350) * (0.37))
        print("37% tax bracket, taxes owed: $" + str(federal_taxes_owed))
    

#clear_terminal()
federal_tax_calculator(9000000)



