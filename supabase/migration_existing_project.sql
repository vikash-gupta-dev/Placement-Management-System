-- Use this ONLY if you already ran the older schema.sql in your existing project.
alter table public.students add column if not exists password text default 'demo1234';
alter table public.students add column if not exists phone text;
alter table public.students add column if not exists gender text;
alter table public.students add column if not exists linkedin_url text;
alter table public.students add column if not exists leetcode_url text;
alter table public.students add column if not exists github_url text;
alter table public.students add column if not exists city text;
alter table public.students add column if not exists bio text;
alter table public.students add column if not exists resume_url text;
alter table public.students add column if not exists skills text[] default '{}';
update public.students set password='demo1234' where password is null;
