db.auth('root', 'admin');

db.createUser({
    user: 'chatterbot',
    pwd: 'password',
    roles: [
        {
            role: 'readWrite',
            db: 'chatterbot',
        },
    ],
});
