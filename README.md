# Users API

This is the documentation for the users API.

## Description

This code implements a REST API from Users. A user can register by providing username, password, status (active, inactive),  email, 
where the username must be unique. A user can view information about other registered users, such as the username, email and their 
status, without any authorization. A user can delete another user using their username, and this action requires authentication. 
A user can change the status of another user, provided their username, and this action requires authentication as well. 
Authentication can be done by providing username and password or, by requesting a token and providing the token instead.

## Endpoints

* `\api\users`

Get all users information. [GET]

* `\api\register`

Register in the system. The user is required to provide `username`, `password`, and `email`. [POST]

* `\api\token`

Request a token. [Authetication Required] [GET]

* `\api\delete\{username}`

Delete a the user with the provided `username`. [Authentication Required] [DELETE]

* `\api\activate\{username}`

Activate the user with the provided `username`. [Authentication Required] [PUT]

* `\api\deactivate\{username}`

Deactivate the user with the provided `username`. [Authentication Required] [PUT]
