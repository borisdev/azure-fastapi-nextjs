import { Inter, Lusitana, Roboto_Flex } from 'next/font/google';

    
export const robotoFlex = Roboto_Flex({ 
    subsets: ['latin'],
    variable: '--font-roboto-flex',
  });
export const lusitana = Lusitana({
  weight: ['400', '700'],
  subsets: ['latin'],
});

 
export const inter = Inter({ subsets: ['latin'] });
