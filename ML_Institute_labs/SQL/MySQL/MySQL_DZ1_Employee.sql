-- Запрос на удаление базы данных, если она существует
DROP DATABASE IF EXISTS employee;

-- Запрос на создание базы данных         
CREATE DATABASE employee;

-- Выбор созданной базы данных для дальнейших операций    
USE employee;

-- Создание таблицы department 
CREATE TABLE department (
    departmentID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,   
    name VARCHAR(30)
) ENGINE=InnoDB;
-- ENGINE=InnoDB;

-- эта таблица аналогичная таблице employee, мы её потом удаляем                     
create table employee1
(employeeID int not null auto_increment primary key,
name1 varchar (80),
job varchar(30),
departmentID int not null
references department(departmentID)
) ENGINE=InnoDB;

-- эта таблица аналогичная таблице employee1, мы её потом не удаляем   
create table employee
(employeeID int not null auto_increment primary key,
name1 varchar (80),
job varchar(30),
departmentID int not null ,
CONSTRAINT `DEP` FOREIGN KEY (departmentID)
REFERENCES department(departmentID)
ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


-- занимаемся добавлением элементов в созданные таблицы  
INSERT INTO department (departmentID, name)
VALUES
   (1, 'Dep_analit'),
    (2, 'Dep_prog'),
    (3, 'Dep_admin');

   
INSERT INTO employee1 (employeeID, name1, job, departmentID)
VALUES
   (100, 'Smit N', 'Programmer', 2),
   (101, 'Stone J.', 'manager', 3),
   (102, 'Asser M.', 'analitic', 1),
   (103, 'Wood N.', 'Programmer', 2),
   (104, 'Thomson L.', 'Programmer', 2);
   

  
INSERT INTO employee (employeeID, name1, job, departmentID)
VALUES
   (100, 'Smit N', 'Programmer', 2),
   (101, 'Stone J.', 'manager', 3),
   (102, 'Asser M.', 'analitic', 1),
   (103, 'Wood N.', 'Programmer', 2),
   (104, 'Thomson L.', 'Programmer', 2);


  
 -- Должно выдавать ошибку (это проверяем)
INSERT INTO employee1 (employeeID, name1, job, departmentID)
values 
	('Wirt C','Programmer',5);

 -- Так же должно выдавать ошибку (это проверяем)                  
INSERT INTO employee (employeeID, name1, job, departmentID)
values 
	('Wirt C','Programmer',5);

 -- Без ошибки (удаляем строку)                         
INSERT INTO department (departmentID, name)
values
    (10,'Test DELETE');

  
 -- Должно выдавать ошибку (это проверяем)
INSERT INTO employee (employeeID, name1, job, departmentID)   
values 
('Wirt C','Programmer',10);


SELECT * FROM department;                
SELECT * FROM employee;                                       

-- Проверяем содержимое таблиц department и employee 
-- после удаления из него кортежа (10, 'Test DELETE')

delete from department where (departmentID, name) = (10,'Test DELETE'); 

SELECT * FROM department;           
SELECT * FROM employee;                                     

DROP TABLE employee1;                   



-- Создание таблицы employeeSkills
CREATE TABLE employeeSkills (
	employeeID int not null
	references employee(employeeID),
	skill VARCHAR(15),
	PRIMARY KEY (employeeID, skill)
) ENGINE=InnoDB;

-- Создание таблицы client
CREATE TABLE client (
	clientID int not null auto_increment primary key,
	name VARCHAR(40),
	adress VARCHAR(100),
	contactPerson VARCHAR(80),
	contactNumber  VARCHAR(80)
    ) ENGINE=InnoDB;

-- Создание таблицы assignment
CREATE TABLE assignment (
	clientID int not null
	references client(clientID),
	employeeID int not null
	references employee(employeeID),
	workdate date,
	hours float,
	PRIMARY KEY (clientID, employeeID, workdate)
    ) ENGINE=InnoDB;

   
   
  INSERT INTO employeeSkills (employeeID, skill)        
VALUES
   (101	, 'Basic'),
   (103, 'Python'),
   (102, 'SQL'),
   (100, 'C++'),
   (100, 'Pascal'),
   (104, 'Delphi'); 
   
   
  INSERT INTO client (clientID, name, adress, contactPerson, contactNumber)     
VALUES
   (1100, 'ACER', 'M. 12 st.', 'Nora', 112233445566),
   (1101, 'MTS', 'S.P.11 st', 'Lena', 665544332211),
   (1102, 'Dog', 'N.N 13 st.', 'Ivan', 123456123456),
   (1103, 'Cat', 'K. 14 st.', 'Petr', 654321123456); 
   
  INSERT INTO assignment (clientID, employeeID, workdate, hours)           
VALUES
   (1100, 100, '2009-01-10', 120),
   (1101, 101, '2008-11-01', 10),
   (1102, 102, '2009-12-10.', 70),
   (1103, 102, '2009-02-01', 100);  
  
  
  -- 1
  -- Получить названия отделов из отношения department.
   select name from department;
   
   
    -- Получить имена всех клиентов и имена сотрудников для
	-- контакта из отношения client1
	SELECt name, contactPerson
FROM client WHERE contactNumber='665544332211';
  
  
  -- 2 Получить для всех служащих отдела № 2 имя сотрудника и 
  -- его должность (атрибут job).МГ
  select name1, job 
  from employee Left join department 
  on employee.departmentID = department.departmentID
  where employee.departmentID = 2;
 
 -- 3 Получить имя служащего, которому было поручено работать 
 -- с клиентом ‘MTS’.
 select contactPerson 
 from client 
 where name = 'MTS'; 
   
  -- 4 Получить название отдела, где работает сотрудник Smit N   
  select name
  from employee Left join department 
  on employee.departmentID = department.departmentID	
  where name1 = 'Smit N';  
  
  -- 5 Выяснить имена служащих, работающих вместе со Smit N, Smit N  
  -- в результат не включать
  SELECt e2.name1 FROM employee as e1, employee as e2 WHERE
  e1.name1 = 'Smit N' AND e1.departmentID = e2.departmentID
  and e2.name1 <> 'Smit N';
 
  -- 6 Создайте запрос, возвращающий имя служащего и всю информацию 
  -- о его (или ее) квалификации (skill).
  select name1, skill 
  from employee as emp, employeeskills as empsk
  where emp.employeeID = empsk.employeeID;

 /*7
Создайте запрос, возвращающий имя служащего и всю
информацию о его (или ее) квалификации (skill).
Создайте запрос, использующий LEFT JOIN и             
возвращающий список клиентов, для которых не было
выделено служащих, работающих с ними.
 */
 select c.name
 from client as c left join 
 assignment as a on c.clientID = a.clientID 
 where employeeID is null;
 
 
 
 -- 8 (a) Добавить в таблицу employee столбец AGE (возраст), salary       
 -- (зарплату), perks (надбавки)
 -- ALTER TABLE employee ADD COLUMN Age INT, ADD COLUMN
 -- salary INT, ADD COLUMN perks INT;
alter table employee
add column age int, 
add column salary int, 
add column perks int; 
 
 
  /* 8(b)
	 Заполнить новые столбцы данными (зарплата: 20000 -50000,   
	надбавки: 1000 – 5000, возраст 20-45 лет).
	Например:
	UPDATE employee SET Age=25,salary=35000, perks=4000 WHERE
	employeeID=100;
  */ 
update employee 
set age = 25, salary = 35000, perks=4000 WHERE
	employeeID=100;
update employee 
set age = 30, salary = 45000, perks=2000 WHERE
	employeeID=101;	
update employee 
set age = 33, salary = 33000, perks=3600 WHERE
	employeeID=102;
update employee 
set age = 48, salary = 30000, perks=3000 WHERE
	employeeID=103;
 update employee 
set age = 27, salary = 47000, perks=4500 WHERE
	employeeID=104;
 
  /* 8(c)
	Добавить в таблицу employee сотрудников, которые являются                 
 	системными программистами и программистами -
	администраторами баз данных. Например, ‘syst.programmer’,
	‘admin. Programmer’
  */ 
insert into employee(name1, job, departmentID, age, salary, perks) values
("Grishin Egor", "syst.programmer", 2, 35, 50000, 4999),
("Kiselev Artem", "admin.Programmer", 1, 38, 49000, 4001);


 -- 9 Вывести все идентификационные номера и имена сотрудников   
 -- возраст которых от 32 до 40 лет (включительно).
 select employeeID, name1
 from employee e
 where age between 32 and 40;



 /* 10 Выбрать имена всех сотрудников, которые не являются
программистами (любыми, системными, прикладными и т.п.).
Указание. Использовать NOT LIKE '%progr%'; */
 select name1
 from employee 
 where job not like "%progr%";



 /* 11 Выбрать имена всех сотрудников в возрасте 25 лет, которые не  
являются программистами. */
  select name1
 from employee 
 where job not like "%progr%"
 and age = 25;




 /* 12 Найти зарплаты и надбавки для каждого программиста и каждого    
аналитика.
SELECT Job,salary,perks FROM employee WHERE Job='programmer'
OR Job='analitic’;*/
 update employee 
 set salary = salary*1.1, perks = perks*1.05
 where job = "programmer";
 update employee 
 set salary = salary*1.1, perks = perks*1.05
 where job = "analitic";
 select salary, perks from employee 
 where job = "programmer" or job = "analitic";
 select name1, salary + perks from employee 
 where job = "programmer";
 




 /* 13 a) Вычислить средний возраст сотрудников компании. Вычислить среднюю зарплату.*/
 select avg(age), avg(salary) from employee;



 /* 14 Сколько компания тратит на зарплату сотрудников по 
подразделениям ?*/
 select departmentID, sum(salary)
 from employee group by departmentID;




 /* 15 Подсчитать число сотрудников имеющих определенную     
должность*/
 select count(*) as "number"
 from employee 
 where job = "programmer";




 /* 16 Вывести сумму всех возрастов сотрудников, работающих в    
компании*/
 select sum(age)
 from employee;




 /* 17 Вычислите сумму зарплат и средний возраст сотрудников, 
которые занимают должность "программист".*/
 select sum(salary), avg(age)
 from employee 
 where job = "programmer";
 




 /* 18 Что делает следующий оператор?                        
SELECT (SUM(perks)/SUM(salary) * 100) FROM employee; */
 select (sum(perks)/sum(salary)*100)
 from employee ;




 /* 19 Подсчитайте количество сотрудников в группах одного  
возраста.*/
 select age, count(*) as "number"
 from employee 
 group by age; 




 /* 20 Найдите средний возраст сотрудников в различных                     
подразделениях (должностях).*/
 select departmentID, avg(age)
 from employee 
 group by departmentID;




 /* 21 Подсчитайте средний возраст сотрудников по должностям с     
использованием псевдонима столбца, отсортируйте по
возрасту.
Задать псевдоним для столбца, содержащего среднее
значение возраста надо, чтобы его можно было сортировать*/
 select job, avg(age) as avg_age
 from employee 
 group by job 
 order by avg_age;




 /* 22 Разница между приведенными ниже запросами 1 и 2
заключается в том, что
а) никакой разницы нет;
б) они возвращают разные данные;
в) они возвращают одни и те же данные, но LEFT JOIN (1), скорее
всего, будет выполняться быстрее;
г) они возвращают одни и те же данные, но подзапрос (2),
скорее всего, будет выполняться быстрее.
Запрос 1:
SELECT employee.name , e.employeeID FROM employee
left join assignment
on employee.employeeID = assignment.employeeID
WHERE clientID is null;
Запрос 2:
SELECT e.name, e.employeeID FROM employee e
WHERE not exists
(SELECT *FROM assignment WHERE employeeID = e.employeeID);*/ 
 
-- 1 запрос 
select employee.name1, employee.employeeID                                        
from employee left join assignment
on employee.employeeID = assignment.employeeID 
where clientID is null;



-- 2 запрос
select e.name1, e.employeeID              
from employee e 
where not exists 
(select * from assignment
where employeeID = e.employeeID);




 /* 23 Создайте запрос, возвращающий имя служащего и всю
информацию о его (или ее) квалификации (skill)*/
 select e.name1, e2.skill 
 from employee e, employeeskills e2 
 where e.employeeID = e2.employeeID; 




 /* 24 Создайте запрос, использующий ключевое слово EXISTS и
возвращающий список клиентов, для которых не было
выделено служащих, работающих с ними.*/
 select c.name 
 from client as c
 where not exists 
 ( select a.employeeID
 from assignment a
 where a.clientID = c.clientID);




 /* 25 Создайте запрос возвращающий имя, возраст и должность
самого старого служащего, с использованием группирующей
функции MAX в подзапросе*/
 select  name1 , age , job 
 from   employee  
 where age = (select max(age) from employee);
 




 /* 26 Снять надбавки со служащих, которые не имели внешних   
заданий (использовать UPDATE и SELECT). */
update employee 
set perks = 0
where not exists
(select name1 where employeeID in 
(select employeeID from assignment));





 /* 27 Добавить в таблицу department столбец ManagerID (номер
руководителя отдела). */
 alter table department 
 add column 
 ManagerID int not null references emploee(emploeeID);
 update department 
 set ManagerID = 111
 where departmentID in (1, 2);
 update department 
 set ManagerID = 101 where departmentID = 3;




 /* 28 Найти номера, имена, номера отделов и имена руководителей 
отделов служащих, размер заработной платы которых меньше
25000 руб.*/
 select e.employeeID, e.name1, d.departmentID, e2.name1 
 from employee e, department d, employee e2 
 where e.departmentID = d.departmentID and 
 d.departmentID = e2.departmentID and 
 e.salary < 25000;





 /* 29 Найти номера отделов и имена сотрудников, размер заработной
платы которых превышает размер заработной платы
руководителя отдела */
 select e.departmentID, e.name1 
 from employee e, department d, employee e2 
 where e.departmentID = d.departmentID and 
 d.ManagerID = e2.employeeID and 
 e.salary > e2.salary; 





 /* 31 Найти номера отделов, все сотрудники которых имеют разный  
возраст, т.е возраст каждого сотрудника уникален
 select e.departmentID */
select e.departmentID 
 from employee as e,
 (select departmentID, count(*) as emp_n
 from employee group by departmentID) as empln,
 (select e2.departmentID, count(e2.age) as un_n
 from employee as e2
 where not exists 
 (select e2.employeeID
 from employee as e3
 where e3.age = e2.age and 
 e3.employeeID != e2.employeeID)
 group by e2.departmentID) as un 
 where e.departmentID = empln.departmentID and 
 empln.departmentID = un.departmentID and 
 empln.emp_n = un_n
 group by e.departmentID;

 

 /* 32 Найти номера отделов, сотрудников которых можно различить по 
имени и возрасту, т.е каждый сотрудник имеет уникальное имя и
возраст. */
 select e.departmentID 
 from employee as e,
 (select departmentID, count(*) as emp_n
 from employee group by departmentID) as empln,
 (select e2.departmentID, count(e2.name1) as un_n
 from employee as e2
 where not exists 
 (select e2.employeeID
 from employee as e3
 where e3.age = e2.age and 
 e3.employeeID != e2.employeeID)
 group by e2.departmentID) as un 
 where e.departmentID = empln.departmentID and 
 empln.departmentID = un.departmentID and 
 empln.emp_n = un_n
 group by e.departmentID;


 

 /* 33. Найти номера и имена сотрудников-однофамильцев (в пределах пред- 
приятия. */
 select e.employeeID, e.name1
 from employee e
 where e.name1 = some 
 (select e2.name1 
 from employee e2
 where e2.employeeID != e.employeeID);
 
 
 
  /* 34. Найти номера и имена сотрудников, не имеющих однофамильцев (в  
пределах предприятия. */
 select e.employeeID, e.name1 
 from employee e
 where e.name1 <> some 
 (select e2.name1 from employee e2
 where e2.employeeID != e.employeeID);
 
 


  /* 34. Найти номера отделов и средний возраст служащих для отделов с  
минимальным средним возрастом служащих */
 select avg_e.departmentID, avg_e.age as avg_age
 from (select e.departmentID, avg(e.age) as age
 from employee as e 
 group by e.departmentID) as avg_e
 where avg_e.age = (select min(apd.age)
 from (select e2.departmentID, avg(e2.age) as age 
 from employee e2
 group by e2.departmentID) as apd);
 
  /* 35. Найти общее число служащих и максимальный размер зарплаты в
отделах с одинаковым максимальным размером зарплаты */
 select sum(t1.departmentID) as number_emp, max(t1.salary) as max_salary  
 from (select e2.departmentID, max(e2.salary) as salary 
 	   from employee e2 
 	   group by e2.departmentID) as t1,
 	   (select e2.departmentID, max(e2.salary) as salary 
 	    from employee e2
 	    group by e2.departmentID) as t2 	   
 where t1.salary = t2.salary and 
 t1.departmentID != t2.departmentID;

  /* 36. Найти имена, номера отделов и имена руководителей отделов в которых,  
размер заработной платы служащих меньше 55000 руб. */
 select d.name, d.departmentID, e.name1
 from department as d, employee as e
 where d.ManagerID = e.employeeID and 
 exists (select e2.name1 
 		 from employee e2 
 		 where e2.salary < 55000 and
 		 e2.departmentID = d.departmentID);
 

  
  
  
  
  
  

