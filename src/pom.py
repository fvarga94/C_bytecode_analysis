            for encap in capsules[0:-1]:
                stop=0
                found_i=0
                while(stop==0):
                    k=found
                    if encap in pom_str[found_i:]:
                        found+=1
                        found_i=pom_str.find(encap,found_i)
                        found_l.append((found_i,encap))
                        found_i+=2
                    else:
                        stop=1
                    if k==found:
                        stop=1
            found_l=sorted(found_l, key=lambda tup: tup[0])
            if len(found_l)>1:
                for f in range(len(found_l[:-1])):
                    pom_lab=[x for x in lab]
                    fi=found_l[f][0]
                    encap=found_l[f][1]
                    start_end[encap].append([level,line_num,-1])
                    pom_lab.append(encap+"_"+str(level))
                    pom_lab[0]-=pom_str[pom_str.find(encap,fi)+1:].count("\n")
                    labels.append(pom_lab)
                    pom_lab=[x for x in lab]
                    for j in range(len(start_end[encap])):
                        if start_end[encap][j][0]==level and start_end[encap][j][2]==-1:
                            #print (start_end[x][j])
                            nn=pom_str[pom_str.find(";",pom_str.find(")",fi)):].count("\n")
                            start_end[encap][j][2]=line_num-nn
                            pom_lab.append(encap+"_"+str(level))
                            pom_lab[0]-=nn
                    labels.append(pom_lab)
