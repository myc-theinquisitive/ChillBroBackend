def get_employee_details(employee_ids):
    from UserApp.exportapi import get_employee_details
    employees = get_employee_details(employee_ids)
    employee_data = {}
    for employee in employees:
        employee_data[employee["id"]] = employee
        employee.pop("id")
    return employee_data
