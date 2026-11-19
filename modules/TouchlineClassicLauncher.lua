-- Adds the companion app shortcut to each career menu.
local m = {version="0.1.3"}
local classic = true
local k, user, shell, base
local ready, apps = {}, {}
local career, classic_visual
local visual_request="common\\menu\\general\\modemainmenufl.bin"
local function number(value) return tonumber(ffi.cast("uintptr_t", value)) end
local function ptr(value) return ffi.cast("void *", value) end
local function u64(address) return tonumber(memory.unpack("u64", memory.read(address, 8))) end
local function decode(hex) return (hex:gsub("..", function(byte) return string.char(tonumber(byte,16)) end)) end
local function relocate(code, index, value)
    local marker = memory.pack("u64", 0x111111110000 + index)
    -- Lua patterns stop at embedded NUL bytes. Relocations require an exact
    -- eight-byte search, including the zero bytes in these marker values.
    local at=assert(code:find(marker,1,true),"Missing launcher relocation")
    assert(not code:find(marker,at+#marker,true),"Duplicate launcher relocation")
    local replacement=memory.pack("u64",value)
    assert(#replacement==#marker,"Invalid launcher pointer width")
    return code:sub(1,at-1)..replacement..code:sub(at+#marker)
end
local function protect_write(address, bytes)
    local old, scratch = ffi.new("uint32_t[1]"), ffi.new("uint32_t[1]")
    if k.VirtualProtect(ptr(address), #bytes, 4, old) == 0 then return false end
    memory.write(address, bytes)
    local valid = memory.read(address,#bytes) == bytes
    return k.VirtualProtect(ptr(address), #bytes, old[0], scratch) ~= 0 and valid
end
local function allocate(code)
    local address = number(memory.allocate_codecave(#code))
    memory.write(address, code)
    if memory.read(address,#code) ~= code
       or k.FlushInstructionCache(k.GetCurrentProcess(),ptr(address),#code) == 0 then return end
    return address
end
local model_specs = {
    ml = {table=40561416, original={12086880,12085808,12086848,12087232}, identity=106},
    bal = {table=40612184, original={12314752,12314624,12086848,12087232}, identity=111},
}
local function menu_rows(ids)
    local bytes={}
    for i=1,11 do bytes[i]=memory.pack("u32",ids[i] or 0) end
    return table.concat(bytes)
end
local function mount_models()
    for mode, spec in pairs(model_specs) do
        if apps[mode] then
            for index, offset in ipairs(spec.original) do
                if u64(base+spec.table+index*8) ~= base+offset then
                    log("TOUCHLINE LAUNCHER disabled: model table differs")
                    return false
                end
            end
        end
    end
    for mode, spec in pairs(model_specs) do
        if apps[mode] then
            local code = decode("83fa6f0f8506000000b801000000c348b80000111111110000ffe083fa6f0f850f000000488d054a0000000f1000410f1100c348b80100111111110000ffe083fa6f0f8506000000b801000000c348b80200111111110000ffe083fa6f0f8506000000b800000000c348b80300111111110000ffe06f00000072010b000000000000000000746f7563686c696e6500")
            code=code:gsub("\x83\xfa\x6f",function() return "\x83\xfa"..string.char(spec.identity) end)
            for index, offset in ipairs(spec.original) do code=relocate(code,index-1,base+offset) end
            local address = allocate(code)
            if not address then return false end
            local label = classic and mode=="bal" and 0x000B01A7 or 0x000B0172
            memory.write(address+117,memory.pack("u32",spec.identity)..memory.pack("u32",label))
            memory.write(address+117+8,memory.pack("u64",address+133))
            local offsets = {0,27,63,90}
            local values = {}
            for _, offset in ipairs(offsets) do values[#values+1]=memory.pack("u64",address+offset) end
            if not protect_write(base+spec.table+8,table.concat(values)) then return false end
        end
    end
    return true
end
local function mount(mode)
    local app = apps[mode]
    if ready[mode] or not app then return end
    local system, event, submenu, expected, submenu_rows
    if mode=="ml" then
        system, event = base+0x26AE3E8, base+0x26AE928
        expected={8,64,65,66,106,67,classic and 0 or 2,0,0,0,0}
        if classic then
            submenu=base+0x26AE390
            submenu_rows={5,59,50,46,49,47,57}
        end
    else
        system, event = base+0x26BAC68, base+0x26BAF78
        expected={8,64,65,105,67,110,classic and 0 or 2,0,0,0,0}
        if classic then
            -- 108 is the native BAL Player Menu category.
            submenu=base+0x26BABB8
            submenu_rows={108,59,98,19,22,23,99}
        end
    end
    local before=menu_rows(expected)
    if memory.read(system,#before) ~= before then return end
    local submenu_before,submenu_after
    if submenu then
        submenu_before=menu_rows(submenu_rows)
        if memory.read(submenu,#submenu_before) ~= submenu_before then return end
        submenu_rows[8]=model_specs[mode].identity
        submenu_after=menu_rows(submenu_rows)
    end
    local original=u64(event)
    if (original==base+0xCD3BF0)~=classic then return end
    local code=decode("5356574883ec504889cf4889d64885d20f8409010000817a08007008010f85fc000000488b4a104839f90f841600000048398f480700000f85e20000004885c90f84d900000048b80d00111111110000ffd089c3488b87400700004885c00f84bb000000488b40104885c00f84ae000000488b4820482b481848c1e9034839cb0f8399000000488b4018488b04d883386f0f858800000031c948ba080011111111000048b80900111111110000ffd04885c00f842b0000004889c34889c1ba0900000048b80a00111111110000ffd04889d948b80b00111111110000ffd0e93400000031c931d249b806001111111100004531c948b807001111111100004889442420c74424280100000048b80c00111111110000ffd04883c4505f5e5bc34889f94889f24883c4505f5e5b48b80400111111110000ffe0")
    code=code:gsub("\x83\x38\x6f",function() return "\x83\x38"..string.char(model_specs[mode].identity) end)
    local values={
        [4]=original,[6]=number(app.executable),[7]=number(app.directory),
        [8]=number(app.title),[9]=number(user.FindWindowW),[10]=number(user.ShowWindow),
        [11]=number(user.SetForegroundWindow),[12]=number(shell.ShellExecuteW),
        [13]=base+0xE3D120,
    }
    for index,value in pairs(values) do code=relocate(code,index,value) end
    local address=allocate(code)
    if not address then return end
    if mode=="bal" and not classic then expected[8]=111 end
    if mode=="ml" and classic then expected[5],expected[6]=67,0 end
    if not protect_write(event,memory.pack("u64",address)) then return end
    local system_after=menu_rows(expected)
    if (system_after~=before and not protect_write(system,system_after))
        or (submenu and not protect_write(submenu,submenu_after)) then
        if submenu then protect_write(submenu,submenu_before) end
        if system_after~=before then protect_write(system,before) end
        protect_write(event,memory.pack("u64",original))
        return
    end
    ready[mode]=true
    log("TOUCHLINE LAUNCHER ready in "..mode)
end
local function track_flow(ctx, filename)
    if type(filename)~="string" then return end
    local name=filename:lower():gsub("/","\\")
    if name=="common\\script\\flow\\ml\\mlmainmanu.json" then
        career="ml"
        mount("ml")
    elseif name=="common\\script\\flow\\bl\\blmainmenu.json" then
        career="bal"
        mount("bal")
    elseif name:find("common\\script\\flow\\topmenu\\",1,true)==1
        or name:find("common\\script\\flow\\league\\",1,true)==1
        or name:find("common\\script\\flow\\compe\\",1,true)==1 then
        career=nil
    end
    return name
end
function m.get_filepath(ctx, filename)
    if track_flow(ctx,filename)==visual_request and career then return classic_visual end
end
function m.make_key(ctx, filename)
    local path=m.get_filepath(ctx,filename)
    if path then return "touchline-classic:"..path end
end
function m.data_ready(ctx, filename)
    track_flow(ctx,filename)
end
function m.init(ctx)
    if classic then
        local path=(ctx.sider_dir or "").."modules\\TouchlineClassicML.bin"
        local visual=io.open(path,"rb")
        if visual then
            visual:close()
            classic_visual=path
        end
        ctx.register("livecpk_make_key",m.make_key)
    end
    ctx.register("livecpk_get_filepath",m.get_filepath)
    ctx.register("livecpk_data_ready",m.data_ready)
    if not ffi then log("TOUCHLINE LAUNCHER needs LuaJIT extensions");return end
    ffi.cdef[[
        void * __stdcall GetModuleHandleA(const char *);
        void * __stdcall GetCurrentProcess(void);
        int __stdcall VirtualProtect(void *,size_t,uint32_t,uint32_t *);
        int __stdcall FlushInstructionCache(void *,const void *,size_t);
        void * __stdcall FindWindowW(const uint16_t *,const uint16_t *);
        int __stdcall ShowWindow(void *,int);
        int __stdcall SetForegroundWindow(void *);
        void * __stdcall ShellExecuteW(void *,const uint16_t *,const uint16_t *,const uint16_t *,const uint16_t *,int);
    ]]
    k,user,shell=ffi.load("kernel32"),ffi.load("user32"),ffi.load("shell32")
    base=number(k.GetModuleHandleA(nil))
    if classic and (memory.read(base+0xE3D120,8)~="\x48\x8b\x81\x88\x00\x00\x00\x8b"
        or memory.read(base+0xCD3BF0,8)~="\x48\x8b\xc4\x56\x57\x41\x56\x48") then
        log("TOUCHLINE LAUNCHER disabled: career menu functions differ")
        return
    end
    local function wide(text)
        local units={}
        local index=1
        while index<=#text do
            local lead=text:byte(index)
            local value, width
            if lead<128 then value,width=lead,1
            elseif lead>=194 and lead<=223 then value,width=lead-192,2
            elseif lead>=224 and lead<=239 then value,width=lead-224,3
            elseif lead>=240 and lead<=244 then value,width=lead-240,4
            else return end
            for offset=1,width-1 do
                local byte=text:byte(index+offset)
                if not byte or byte<128 or byte>191 then return end
                value=value*64+byte-128
            end
            if value==0 or value>0x10FFFF or value>=0xD800 and value<=0xDFFF
               or width==2 and value<128 or width==3 and value<2048 or width==4 and value<65536 then return end
            if value>=65536 then
                value=value-65536
                units[#units+1]=0xD800+math.floor(value/1024)
                units[#units+1]=0xDC00+value%1024
            else units[#units+1]=value end
            index=index+width
        end
        local buffer=ffi.new("uint16_t[?]",#units+1)
        for offset,value in ipairs(units) do buffer[offset-1]=value end
        buffer[#units]=0
        return buffer
    end
    local sider_dir=ctx.sider_dir or ""
    local function find_app(name, folders)
        for _, folder in ipairs(folders) do
            local path=sider_dir..folder..name..".exe"
            local file=io.open(path,"rb")
            if file then
                file:close()
                local executable=wide(path)
                local directory=wide(folder=="" and sider_dir or sider_dir..folder:sub(1,-2))
                local title=wide(name)
                if executable and directory and title then
                    return {executable=executable, directory=directory, title=title}
                end
            end
        end
        log("TOUCHLINE LAUNCHER missing "..name..".exe")
    end
    apps.ml=find_app("Touchline",{"TouchlineCompanion\\"})
    if classic then
        apps.bal=find_app("Prologue",{"PrologueCompanion\\","Prologue\\","TouchlineCompanion\\",""})
    else
        apps.bal=apps.ml
    end
    if not apps.ml and not apps.bal then return end
    if not mount_models() then apps={}; return end
    log("TOUCHLINE LAUNCHER initialized")
end
return m
