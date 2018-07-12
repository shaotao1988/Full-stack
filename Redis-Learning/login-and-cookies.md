# Login and cookie caching

- Signed cookies  

Typically store the user's name, user ID, the time they last logged in,  and whatever else useful.  
The cookie also includes a signature that allows the server to verify the information that the browser sent hasn't been altered.  
Pros: Everything needed to verify the cookie is in the cookie, additional information can be included and signed easily.  
Cons: Correctly handling signatures is hard, and it's easy to forget to sign or verify data.  

- Token cookies  

Uses a series of random bytes as the data in the cookie.  
On the server, the token is used as a key to look up the user who owns that token by querying a database.  
Over time, old tokens can be deleted to make room for new tokens.  
Pros: Adding information is easy, mobile and slow clients can send requests faster becasuse of small cookies
Cons: More information to store on server. Query a relation dabase could be expensive

