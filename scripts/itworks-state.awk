# POSIX awk; all diagnostics contain fixed safe text, never user state values.
function trim(s) { sub(/^[ \t]+/, "", s); sub(/[ \t]+$/, "", s); return s }
function enc(s) { gsub(/%/, "%25", s); gsub(/\t/, "%09", s); gsub(/\r/, "%0D", s); gsub(/\n/, "%0A", s); return s }
function diag(kind, code, msg, path, line) {
    if (path == "") path = file
    if (line == "") line = FNR
    print kind "\t" code "\t" enc(path) "\t" line "\t" enc(msg)
    if (kind == "ERROR") errors++; else if (kind == "WARN") warnings++; else blocks++
}
function heading(s) { sub(/[ \t]+#+[ \t]*$/, "", s); return trim(s) }
function closure(s) { return s ~ /^(Closed|Verified|Accepted):? [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]:[ \t]*[^ \t]/ }
function boundary(s,    j,ticks,last,tail) {
    for(j=1;j<=length(s);j++) {
        if(substr(s,j,1)=="`") ticks=!ticks
        if(!ticks && substr(s,j,3)==" | ") {
            tail=substr(s,j+3)
            if(tail ~ /^(Evidence to close:|Closed:? |Verified:? |Accepted:? )/) last=j
        }
    }
    return last
}
function drift(open,sev,msg) {
    diag(open ? "ERROR" : "WARN",open ? "E_FINDING_SYNTAX" : "W_CLOSURE_MISSING",msg)
    if(!open && sev=="CRITICAL" && op!="check") diag("BLOCKED","B_CLOSURE_MISSING","Critical closure evidence requires review")
    if(!open && index(file,".itworks/archive/")==1 && op=="counts") diag("ERROR","E_FINDING_SYNTAX","Archived finding is malformed")
}
function finding(s,    open,rest,sev,lens,p,desc,tail,i,mark) {
    open = s ~ /^[ \t]*[-*+][ \t]+\[ \]/
    if (s !~ /^- \[[ x]\] (CRITICAL|IMPORTANT|ADVISORY) \| (security-auth|llm-security|real-data|testing|production-readiness) \| /) {
        drift(open,(s ~ /\] CRITICAL([ \t]|$)/ ? "CRITICAL" : ""),"Finding syntax requires review"); return
    }
    rest = substr(s,7); p = index(rest," | "); sev = substr(rest,1,p-1); rest = substr(rest,p+3)
    p = index(rest," | "); lens = substr(rest,1,p-1); rest = substr(rest,p+3)
    if (!open) found++
    p=boundary(rest)
    if(!p) { drift(open,sev,"Finding evidence field is missing or malformed"); return }
    desc=trim(substr(rest,1,p-1)); tail=trim(substr(rest,p+3))
    if (desc == "" || (open && (tail !~ /^Evidence to close: / || trim(substr(tail,19)) == "")) || (!open && !closure(tail))) {
        drift(open,sev,"Finding evidence field is empty or malformed"); return
    }
    if (open) found++
    if (open) {
        open_all++; if (sev != "ADVISORY") open_gate++
        if (sev == "CRITICAL") { critical_open++; if (file == ".itworks/REVIEWS.md") live_critical++ }
    } else if (tail ~ /^Accepted/) {
        accepted++; if (sev == "CRITICAL") critical_accepted++
        accept_n++; accept_desc[accept_n]=desc; finding_matches[desc]++; accept_sev[accept_n]=sev; accept_file[accept_n]=file; accept_line[accept_n]=FNR
    } else fixed++
}
BEGIN {
    print "FORMAT\t1"; op=ENVIRON["ITWORKS_STATE_OP"]
    for(i=1;i<ARGC;i++) { path=ARGV[i]; sub(/^\.\//,"",path); seen[path]=1 }
}
{
    file=FILENAME; sub(/^\.\//,"",file); sub(/\r$/, "", $0); seen[file]=1; lines[file]++
    if (file == ".itworks/PROJECT.md" || file == ".itworks/MAP.md") heads[file SUBSEP heading($0)]=1
    if (file == ".itworks/PROFILE.md") {
        if ($0 ~ /^profile:/) {
            profiles++; v=$0; sub(/^profile:[ \t]*/, "", v); sub(/[ \t]+#.*/, "", v); v=trim(v)
            if (v !~ /^(guided|brief|expert)$/) diag("ERROR","E_PROFILE_VALUE","Profile must be a complete supported scalar")
        }
        if ($0 ~ /^format_version:/) {
            versions++; v=$0; sub(/^format_version:[ \t]*/, "", v); sub(/[ \t]+#.*/, "", v); v=trim(v)
            if (v !~ /^[123]$/) diag("ERROR","E_FORMAT_VERSION","Explicit state version is unsupported")
        }
        if ($0 ~ /^last_audit:/) { audit=1; if ($0 ~ /^last_audit:[ \t]*none([ \t]|$)/) audit_none=1 }
        if ($0 ~ /^last_checkpoint:/ && $0 !~ /@[0-9a-fA-F]+/ && $0 !~ /^last_checkpoint:[ \t]*none([ \t]|$)/) diag("WARN","W_CHECKPOINT_SHA","Checkpoint has no revision identity")
        if ($0 ~ /^  [a-z-]+:/) {
            v=$0; sub(/^  /,"",v); sub(/:.*/,"",v); debt[v]=1
            if (v !~ /^(security-auth|llm-security|real-data|testing|production-readiness)$/) diag("WARN","W_DEBT_UNKNOWN","Unknown lens debt key")
        }
    }
    if (file == ".itworks/DECISIONS.md" && length($0)>600) diag("WARN","W_DECISION_SIZE","Decision exceeds the length guide")
    if (file == "SHIPPED.md") { if ($0 ~ /OUTSTANDING/) outstanding=1; if (tolower($0) ~ /accepted risks/) shipped_accept=1 }
    if (file == ".itworks/REVIEWS.md" || index(file,".itworks/archive/")==1) {
        if (FNR==1) in_accept=0
        if ($0 ~ /^#/) in_accept=(heading($0)=="### Accepted risks")
        if (in_accept && $0 ~ /^-[ \t]/) {
            entries++
            entry=$0
            if (match(entry, / \| User's words: /)) {
                quoted=trim(substr(entry,RSTART+RLENGTH)); sub(/ \| Revisit when:.*/,"",quoted); quoted=trim(quoted)
                if (quoted !~ /^".*"$/ || trim(substr(quoted,2,length(quoted)-2))=="") diag("ERROR","E_ACCEPTANCE_EMPTY","Acceptance requires nonempty quoted user words")
            }
            if (entry !~ /^- [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] \| / || !match(entry, / \| User's words: /)) {
                diag("WARN","W_ACCEPTANCE_LINK","Historical acceptance cannot be linked precisely")
            } else {
                entry_text=substr(entry,1,RSTART-1); sub(/^- [^ ]+ \| /,"",entry_text); entry_text=trim(entry_text)
                words=trim(substr(entry,RSTART+RLENGTH)); sub(/ \| Revisit when:.*/,"",words); words=trim(words)
                if (entry_text=="" || words !~ /^".*"$/ || trim(substr(words,2,length(words)-2))=="") diag("ERROR","E_ACCEPTANCE_EMPTY","Acceptance requires finding text and nonempty quoted user words")
                else entry_matches[entry_text]++
            }
            if ($0 !~ / \| Revisit when:[ \t]*[^ \t]/) diag("WARN","W_REVISIT_MISSING","Acceptance has no revisit condition")
        }
        if ($0 ~ /^[ \t]*[-*+][ \t]+\[[ xX]\]/) finding($0)
        if ($0 ~ /^## / && $0 !~ /^## (Checkpoint [0-9]+|Baseline checkpoint|Closeout sweep|Closeout|Reopen review|Audit|Archive)([ \t]|$|-)/) diag("WARN","W_REVIEW_HEADING","Unrecognized review section heading")
    }
}
END {
    file=".itworks/PROFILE.md"
    if (!profiles) diag("ERROR","E_PROFILE_VALUE","Profile scalar is missing",file,0)
    if (profiles>1) diag("ERROR","E_PROFILE_DUPLICATE","Profile scalar is duplicated",file,0)
    if (versions>1) diag("ERROR","E_FORMAT_VERSION","State version is duplicated",file,0)
    if (!versions) diag("WARN","W_FORMAT_VERSION","Absent format version is legacy v1 drift",file,0)
    if (!audit) diag("WARN","W_AUDIT_MISSING","Legacy state has no audit marker",file,0)
    if (!debt["llm-security"]) diag("WARN","W_DEBT_MISSING","Legacy state has no LLM debt key",file,0)
    n=split("What it is|Who uses it|Terminology map|Stack|Data|Where it will live|Definition of done|Verification expectations",required,"|")
    for (i=1;i<=n;i++) if (!heads[".itworks/PROJECT.md" SUBSEP "## " required[i]]) diag("ERROR","E_PROJECT_HEADING","Required exact project heading is missing",".itworks/PROJECT.md",0)
    if (!seen[".itworks/MAP.md"]) diag("WARN","W_MAP_MISSING","Legacy state has no code map",".itworks/MAP.md",0)
    else {
        n=split("Run|Test|Layout|Environment|Gotchas",required,"|")
        for(i=1;i<=n;i++) if (!heads[".itworks/MAP.md" SUBSEP "## " required[i]]) diag("WARN","W_MAP_HEADING","Code map heading is missing",".itworks/MAP.md",0)
        if(lines[".itworks/MAP.md"]>80) diag("WARN","W_MAP_SIZE","Code map exceeds size guide",".itworks/MAP.md",0)
    }
    if(lines[".itworks/REVIEWS.md"]>800) diag("WARN","W_REVIEWS_SIZE","Consider archiving eligible closed sections",".itworks/REVIEWS.md",0)
    if (accept_n && !entries) diag("ERROR","E_ACCEPTANCE_EMPTY","Accepted finding has no acceptance entry",".itworks/REVIEWS.md",0)
    for (i=1;i<=accept_n;i++) {
        desc=accept_desc[i]
        if (finding_matches[desc]!=1 || entry_matches[desc]!=1) {
            diag("WARN","W_ACCEPTANCE_LINK","Accepted finding has no unique exact acceptance entry",accept_file[i],accept_line[i])
            if(op!="check" && accept_sev[i]=="CRITICAL") diag("BLOCKED","B_ACCEPTANCE_LINK","Critical acceptance linkage requires review",accept_file[i],accept_line[i])
        }
    }
    if(seen["SHIPPED.md"]) {
        if(live_critical) diag("ERROR","E_SHIPPED_CRITICAL","Ship history coexists with open critical findings",".itworks/REVIEWS.md",0)
        if(outstanding && !open_all) diag("WARN","W_SHIPPED_OUTSTANDING","Ship history lists untracked outstanding work","SHIPPED.md",0)
        if(open_gate && !outstanding) diag("WARN","W_SHIPPED_OPEN","Ship history omits outstanding gate findings","SHIPPED.md",0)
        if(accepted && !shipped_accept) diag("WARN","W_SHIPPED_ACCEPTED","Ship history omits accepted risks","SHIPPED.md",0)
        if(audit_none) diag("WARN","W_SHIPPED_AUDIT","Ship history has no recorded whole-application audit","SHIPPED.md",0)
    }
    if(op=="gate" && critical_open) diag("BLOCKED","B_CRITICAL_OPEN","Open critical findings block release",".itworks/REVIEWS.md",0)
    if(op=="counts" && !errors && !blocks) {
        print "COUNT\tfound\t" found+0; print "COUNT\tfixed\t" fixed+0; print "COUNT\taccepted\t" accepted+0
        print "COUNT\tcritical_open\t" critical_open+0; print "COUNT\tcritical_accepted\t" critical_accepted+0
    }
    print "SUMMARY\t" errors+0 "\t" warnings+0 "\t" blocks+0
    exit (errors ? 1 : blocks ? 2 : 0)
}
