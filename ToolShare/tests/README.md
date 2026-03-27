# API Component Tests

## Main APIs in this project

- Auth API: `/login/`, `/logout/`, `/home/`, `/login/credits/`
- Registration API: `/registration/`
- Tools API: `/sharecenter/addtool/`, `/tooldirectory/`, `/sharecenter/tool/<id>/`, `/sharecenter/tool/edit/<id>/`, `/sharecenter/tool/delete/<id>/`, `/sharecenter/tool/changestate/<id>/`
- Sheds API: `/sharecenter/createshed/`, `/sharecenter/shed/<username>/`, `/sharecenter/shedlist/`, `/sharecenter/deleteshed/`
- Users API: `/sharecenter/user/<username>/`, `/sharecenter/userdirectory/`, `/sharecenter/edituser/<username>/`, `/sharecenter/editpassword/`
- Messages API: `/messagecenter/`, `/messagecenter/sendMessage/<user_id>/`, `/messagecenter/message/<message_id>/`, `/messagecenter/delete/<message_id>/`
- Reservations API: `/messagecenter/sendrequest/<tool_id>/`, `/messagecenter/reservations/`, `/messagecenter/reservations/return/<reservation_id>/`, `/messagecenter/reservations/delete/<reservation_id>/`

## Folder layout

- `tests/api/auth_api/`
- `tests/api/registration_api/`
- `tests/api/tools_api/`
- `tests/api/sheds_api/`
- `tests/api/users_api/`
- `tests/api/messages_api/`
- `tests/api/reservations_api/`

Each API folder contains:

- component test module(s)
- a `data/` subfolder for fixture/payload data

## Test naming convention

- Positive case methods use `test_POSITIVE_...`
- Negative case methods use `test_NEGATIVE_...`

## Current TODO policy in tests

You will find explicit `TODO` comments in the component tests for:

- scenarios that are currently untested
- scenarios where API input validation is not currently enforced in the application

## How to run tests

From project root (`ToolShare/`):

```bash
.venv/bin/python manage.py test tests
```

Run only a single API component test module:

```bash
.venv/bin/python manage.py test tests.api.tools_api.test_tools_component
```

Run a single test class:

```bash
.venv/bin/python manage.py test tests.api.reservations_api.test_reservations_component.ReservationsAPIComponentTests
```

Run one test method:

```bash
.venv/bin/python manage.py test tests.api.messages_api.test_messages_component.MessagesAPIComponentTests.test_POSITIVE_DELETE_message
```
