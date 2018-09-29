select * from events limit 10;

select GAME_PA_CT as 'Batters Faced', round(((sum(case when EVENT_CD = 23 then 1 else 0 end)*13)+(sum(case when EVENT_CD = 14 or EVENT_CD = 16 then 1 else 0 end)*3)+(sum(case when EVENT_CD = 3 then 1 else 0 end)*-2))/(count(*)/3),3)+3.2 as 'FIP' from events
where PIT_START_FL = 'T'
group by GAME_PA_CT;

select * from lkup_cd_event;