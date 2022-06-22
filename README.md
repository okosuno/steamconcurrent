# steamconcurrent

<center>
<img src="https://imgur.com/LQW9fp0.png"/>
</br>polybar display</br></br>
<img src="https://i.imgur.com/kf8Bfip.png"/>  
</br>terminal display</br></br>
<img src="https://imgur.com/pACwQDO.png"/>
</br>list view</br></br> 
</center>

#### what it does
tracks multiple steam games for the number of concurrent players online right now for display in terminal or polybar. 

search for, add, and remove games via title or appid.

takes some configuration options such as query and refresh interval.

#### how it does it
this program only queries the steam web api, it doesn't scrape steamdb or any other third-party sites. it fetches a list of every steam game and appid and builds a queriable sqlite db. it then builds a tracking db for each game added.

#### limitations
the steam web api does not provide any historical data for player count. display modes show variance from average using the historical data tracked only since the game was added to the local db. 

it does not include clearing old games from the historical data db when removing games from the list. 

i didn't yet account for steam going down. watch out for those maintenance tuesdays.

#### why did you do it like that
so while i wasn't sure about scraping steamdb.info at first, i honestly wasn't very concerned since the idea of this in my head gave me the chance to exercise different concepts i haven't yet had a reason to use. that said, i will be making a different version of this program that does take advantage of steamdb's massive wealth of data.

ultimately, this version of the program does exactly what i wanted it to do, i'm happy.

#### lessons learned
1. it is a good idea to set up unit testing as you're building the program.  
2. definitely set up debugging from the beginning as well.  
3. sqlite can be onery if you don't properly handle the opening and close of connections.  
4. even though there is no concurrency left in the program, i did explore that as an avenue for querying the database in consistent intervals. i learned a lot about passing data between threads and why it should be avoided.
5. scope creep can be devastating for side projects. write the plan first, deviate as little as possible. multiple reformats makes you wish you just did a rewrite.
6. circular imports are nasty.
7. data serialization is handy.
8. i have a very, very lot to learn.

#### how do it use it

`git clone https://github.com/okosuno/steamconcurrent.git`
`cd steamconcurrent`
`python main_temp.py --help`

1. you'll likely want to run `--setup` first
2. and then start adding games with `--name [query]`
3. or searching for games with `--query --name [query]`
4. check the games you've added with `--list`

after it's set up you can just run whichever mode you want: `-d` or `-p`
