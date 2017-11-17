from MHS.classes import component, componentCollector

a = component.Component(1, 0, 0, 500, 500, 25000, [[0,0],[7,7]])
collect = componentCollector.ComponentCollector()
collect.add_component(a)

d = collect.as_dict
print(d)

b = component.Component(270, 200, 0, 430, 740, 22340, [[0,350],[17,47]])
collect.add_component(a)