#include<stdio.h>

void do_things(void)
{
	int random_var = 2;
	for (int i=0; i<3; i++) random_var *= random_var;
	printf("%d",random_var);
	return;
}

int main()
{
    int test;
    int count=0;
    scanf("%d",&test);
    for (int i=0; i<3; i++)
	for (int j=0; j<3; j++)
	    count+=1;
    while(test--)
    {
        int number,i,leaves=0;
        float branches;
        scanf("%d",&number);

        for(i=0;i<number;i++)
        {
            scanf("%d",&leaves);
            if(i!=0)
            {
                branches*=2;
            }
            else{
                    branches=1;
            }
            branches=branches-leaves;
        }
	do_things();
        if(branches==0)
        {
            printf("Yes\n");
        }
        else{
                printf("No\n");
        }
    }
    printf("%d",count);
    return 0;
}
