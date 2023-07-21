# %%
# w -> write
# r -> read
# a -> 이어쓰기
f = open("Hello.txt","w",encoding="utf-8")
f.write("Hello world\n")
f.write("Hello world\n")
f.write("Hello world\n")
f.write("Hello world\n")
f.close()

with open("Hello.txt","w",encoding="utf-8") as f:
    f.write("Hello world\n")
    f.write("Hello world\n")
    f.write("Hello world\n")
    f.write("Hello world\n")
    #with을 쓰면 close를 안해도 된다. f가 끝나면 자동으로 f지움.


# %%
f = open("Hello.txt","r",encoding="utf-8")
content = f.read()
print(content)
f.close()
