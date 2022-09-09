UPDATE scenario_overview
SET calculationState= 'esdlCreated'
WHERE scenarioUuid = %(scenarioUuid)s