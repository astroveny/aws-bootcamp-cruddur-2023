-- this file was manually created
INSERT INTO public.users (email, display_name, handle, cognito_user_id)
VALUES
  ('woody@gmail.com', 'Woody', 'woody','7659c102-7ad4-44bd-bdc3-208f934d1f41'),
  ('andrew@exampro.co', 'Andrew Brown', 'andrewbrown' ,'7659c102-7ad4-44bd-bdc3-208f934d1f41'),
  ('buzz@gmail.com', 'Buzz Lightyear', 'buzz' ,'MOCK');

INSERT INTO public.activities (user_uuid, message, expires_at)
VALUES
  (
    (SELECT uuid from public.users WHERE users.handle = 'woody' LIMIT 1),
    'This was imported as seed data!',
    current_timestamp + interval '10 day'
  )